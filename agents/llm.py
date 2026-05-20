"""
Thin LiteLLM wrapper used by all agents and metrics.
Swap MODEL / MODEL_JUDGE in config.py to use any LiteLLM-supported provider
(OpenAI, Gemini, OpenRouter, etc.) without touching agent code.

Prompt caching: when cache_system=True the system text is wrapped in a
content-list with cache_control. LiteLLM forwards this to Anthropic and
strips it silently for all other providers.

Retries: transient errors (rate limit, service unavailable, connection, timeout)
are retried up to LLM_MAX_RETRIES times. The wait is max(exponential, Retry-After)
so provider hints are always respected over the backoff schedule.
"""
import re
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import litellm
from tenacity import retry, retry_if_exception_type, stop_after_attempt, RetryCallState
from config import LLM_API_KEY, KEY_FROM_UI, MODEL, MODEL_JUDGE, LLM_MAX_RETRIES, LLM_MIN_INTERVAL, LLM_BACKEND

_last_call: float = 0.0

litellm.set_verbose = False
litellm.suppress_debug_info = True

print(f"LLM model  : {MODEL}")
print(f"Judge model: {MODEL_JUDGE}")

_RETRYABLE = (
    litellm.RateLimitError,
    litellm.ServiceUnavailableError,
    litellm.APIConnectionError,
    litellm.Timeout,
    subprocess.TimeoutExpired,
)

_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[A-Za-z]|\x1b\][^\x07]*\x07')


def _strip_ansi(text: str) -> str:
    return _ANSI_ESCAPE.sub('', text)


def _chat_cli(backend: str, model: str, system: str, user: str) -> str:
    """Shell out to an installed CLI tool instead of calling the API."""
    merged = f"<system>\n{system}\n</system>\n\n{user}" if system else user

    if backend == "claude-cli":
        cmd = ["claude", "-p", merged, "--model", model]
    elif backend == "gemini-cli":
        cmd = ["gemini", "--skip-trust", "-p", merged]
    elif backend == "codex-cli":
        cmd = ["codex", "exec", merged]
    else:
        raise ValueError(f"Unknown CLI backend: {backend!r}")

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(
            f"{backend} exited {proc.returncode}: {(proc.stderr or proc.stdout).strip()}"
        )
    return _strip_ansi(proc.stdout).strip()


def _retry_after_secs(exc: Exception) -> float | None:
    """Parse Retry-After seconds out of the provider error payload if present."""
    m = re.search(r'"retry_after_seconds"\s*:\s*([0-9.]+)', str(exc))
    return float(m.group(1)) if m else None


def _wait(retry_state: RetryCallState) -> float:
    """Exponential backoff floored to the provider's Retry-After hint when given."""
    exc = retry_state.outcome.exception()
    hint = _retry_after_secs(exc) if exc else None
    expo = min(2.0 ** (retry_state.attempt_number - 1), 60.0)
    delay = max((hint + 1) if hint else 0, expo)
    print(
        f"  [retry {retry_state.attempt_number}/{LLM_MAX_RETRIES}] "
        f"{type(exc).__name__} — waiting {delay:.1f}s"
        + (f" (provider hint: {hint:.0f}s)" if hint else "")
    )
    return delay


@retry(
    retry=retry_if_exception_type(_RETRYABLE),
    wait=_wait,
    stop=stop_after_attempt(LLM_MAX_RETRIES + 1),
    reraise=True,
)
def chat(
    model: str,
    system: str,
    user: str,
    max_tokens: int,
    cache_system: bool = False,
    api_key: str | None = None,
    backend: str | None = None,
) -> str:
    effective_backend = backend or LLM_BACKEND
    if effective_backend != "api":
        return _chat_cli(effective_backend, model, system, user)

    global _last_call
    if LLM_MIN_INTERVAL > 0:
        wait = LLM_MIN_INTERVAL - (time.monotonic() - _last_call)
        if wait > 0:
            time.sleep(wait)
        _last_call = time.monotonic()

    system_content = (
        [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        if cache_system else system
    )
    response = litellm.completion(
        model=model,
        max_tokens=max_tokens,
        api_key=api_key if KEY_FROM_UI else (api_key or LLM_API_KEY),
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content.strip()
