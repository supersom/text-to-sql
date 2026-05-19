"""
Thin LiteLLM wrapper used by all agents and metrics.
Swap MODEL / MODEL_JUDGE in config.py to use any LiteLLM-supported provider
(OpenAI, Gemini, OpenRouter, etc.) without touching agent code.

Prompt caching: when cache_system=True the system text is wrapped in a
content-list with cache_control. LiteLLM forwards this to Anthropic and
strips it silently for all other providers.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import litellm
from config import LLM_API_KEY, MODEL, MODEL_JUDGE

litellm.set_verbose = False
litellm.suppress_debug_info = True

print(f"LLM model  : {MODEL}")
print(f"Judge model: {MODEL_JUDGE}")


def chat(model: str, system: str, user: str, max_tokens: int, cache_system: bool = False) -> str:
    system_content = (
        [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        if cache_system else system
    )
    response = litellm.completion(
        model=model,
        max_tokens=max_tokens,
        api_key=LLM_API_KEY,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content.strip()
