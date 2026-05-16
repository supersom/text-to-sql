This requirement document outlines the implementation of a Text-to-SQL AI application, specifically focusing on Phase 1: Golden Dataset Generation and Phase 2: Automated Evaluation Pipeline using Comet OPIK.
1. Project Overview
The objective is to build a reliable, enterprise-grade Text-to-SQL application that translates natural language questions into executable SQL queries
. The system must include a self-improving evaluation loop to ensure accuracy and prevent "confident but wrong" AI failures
.

--------------------------------------------------------------------------------
2. Phase 1: Golden Dataset Generation
The "Golden Dataset" serves as the ground truth for benchmarking the AI's performance
.
Functional Requirements:
SME Question Discovery: Facilitate discovery sessions with domain experts (e.g., Claims Adjusters) to identify the top 10–15 most frequent, high-value business questions
.
Metadata Integration: Ingest table metadata (schemas, column descriptions, and relationships) to ground the generation process
.
LLM Query Variation Engine: Use an LLM to generate at least 50–100 variations per domain question by introducing
:
Paraphrasing and different phrasing styles.
Temporal modifiers (e.g., "last quarter" vs. "since January").
Intentional typos or ambiguity to test robustness.
Ground-Truth Validation: Provide an interface for SMEs to review and validate that the generated SQL correctly captures the business intent
.
Metadata Tagging: Every entry in the dataset must be tagged with
:
Complexity: Simple, Medium, Complex.
SQL Operations: Filter, Join, GroupBy, Subquery.
Risk Level: Low, Medium, High.
Domain: e.g., Insurance, Banking.

--------------------------------------------------------------------------------
3. Phase 2: Automated Evaluation Pipeline (OPIK Integration)
The evaluation pipeline intercepts the agent's output and scores it against the Golden Dataset before it reaches the end user
.
Functional Requirements:
OPIK Experiment Tracking: Integrate Comet OPIK to track every prompt variation and model response as an "experiment"
.
Multi-Dimensional Scoring: Implement three mandatory metrics for every query:
SQL Validity (Heuristic): Does the generated SQL execute without error?
.
Execution Accuracy (Heuristic): Does the result set of the generated SQL match the result set of the ground-truth SQL exactly?
.
Answer Relevance (LLM-as-Judge): Does the response semantically address the user's intent?
.
Ship/No-Ship Thresholds: Implement an automated gate that blocks deployment unless
:
SQL Validity > 90%
Execution Accuracy > 70%
Answer Relevance > 0.75
Continuous Feedback Loop: Capture production signals (user "thumbs up/down" or zero-result queries) and automatically feed them back into the Phase 1 pipeline to expand the Golden Dataset
.

--------------------------------------------------------------------------------
4. Application Architecture
To build this into a small application, the following stack is required:
Frontend: A Streamlit interface for user prompts, risk dashboards, and human-in-the-loop (HITL) approval gates
.
Backend: A FastAPI gateway to handle authentication, PII scrubbing, and request validation
.
Orchestration: LangGraph to manage a multi-agent swarm
:
Planner Agent: Decomposes the user request.
SQL Generator Agent: Translates text to SQL.
Governance Agent: Checks for RBAC and policy compliance
.
Data Layer: PostgreSQL for workflow state and pgvector for schema/knowledge retrieval
.

--------------------------------------------------------------------------------
5. Security & Governance Requirements
Prompt Injection Prevention: The system must sandbox SQL generation to a pre-approved schema subset. Only SELECT statements are authorized; DROP/DELETE/UPDATE operations must be blocked
.
PII Scrubbing: Implement an ingestion-time redaction layer to ensure PII (names, phone numbers) never enters the LLM context or the evaluation logs
.
Observability (MELT): Implement OpenTelemetry (OTel) to generate Metrics, Events, Logs, and Traces for every agent decision and tool call [109.1, 109.2, 109.3].