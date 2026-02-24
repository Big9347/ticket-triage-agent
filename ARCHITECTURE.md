# Architecture Decisions

## Overview

The Support Ticket Triage Agent is a single-pass agentic pipeline that reads a support ticket, gathers context via tool calls, and produces a structured triage decision. It is designed to be readable, maintainable, and easy to extend.

## Architecture

```
┌──────────────┐     ┌───────────────────────┐     ┌─────────────────┐
│  Sample      │────▶│  Agent (agent.py)      │────▶│  TriageResult   │
│  Tickets     │     │  - System prompt       │     │  (Pydantic)     │
│  (data.py)   │     │  - Tool-call loop      │     │                 │
└──────────────┘     │  - JSON parsing        │     └─────────────────┘
                     └───────┬───────┬────────┘
                             │       │
                    ┌────────▼┐   ┌──▼──────────────┐
                    │ Tool 1  │   │ Tool 2           │
                    │ Customer│   │ Knowledge Base   │
                    │ Lookup  │   │ Search           │
                    └─────────┘   └──────────────────┘
```

### Why This Design

1. **Pydantic everywhere** — Every data structure (tickets, customer history, triage results) is a Pydantic model. This gives us validation, serialisation, and self-documenting schemas with no extra effort. The agent's final output is parsed into a `TriageResult` model, catching malformed responses immediately.

2. **Tool-first enrichment** — Instead of dumping all context into the initial prompt, the agent *discovers* context by calling tools. This mirrors how a real support agent works (look up the customer, search the docs) and keeps the prompt focused. It also means adding new data sources is just adding a new tool.

3. **Weighted scoring with breakdown** — The urgency score uses explicit sub-components (customer value, impact, urgency signals, repeat issue, outage boost). This makes the score explainable — a support lead can see *why* a ticket scored 75 — which is critical for adoption. Per the solution.txt guidance: "if scoring isn't explainable, the team ignores it."

4. **Separation of concerns** — `models.py` defines schemas, `data.py` owns data, `tools.py` defines tool interfaces, `agent.py` runs the LLM loop. Each file has a single responsibility and can be modified independently.

## What Could Go Wrong

| Risk | Mitigation |
|---|---|
| **LLM returns invalid JSON** | Retry loop with error feedback — agent.py retries up to 10 times, feeding parse errors back to the model |
| **Hallucinated tool names** | `execute_tool()` validates against a registry and returns a clean error |
| **Inconsistent scoring** | Detailed scoring rubric in system prompt + `temperature=0.2` for deterministic output |
| **Non-English tickets misclassified** | System prompt explicitly handles multilingual tickets; tested with Thai sample |
| **API rate limits / failures** | In production: add exponential backoff, circuit breakers, and fallback to rule-based triage |
| **Sensitive data in prompts** | Tool layer acts as a data access boundary — the agent only sees fields we explicitly expose |

## Production Evaluation Strategy

1. **Accuracy metrics** — Compare agent urgency classifications against human-labelled ground truth on a holdout set. Track precision/recall per urgency level.

2. **Scoring consistency** — Run the same ticket multiple times; measure score variance. Acceptable threshold: ±5 points.

3. **Tool usage audit** — Log every tool call. Flag tickets where the agent skipped tools (likely lower quality). Monitor for unnecessary or repeated tool calls.

4. **Human override rate** — Track how often support reps change the agent's urgency or routing. A high override rate on a specific ticket type signals a prompt or scoring gap.

5. **Latency & cost** — Measure end-to-end triage time and token usage per ticket. Set budgets per triage (e.g., max 4,000 tokens).

6. **A/B testing** — Run agent triage alongside human triage on a percentage of tickets. Compare resolution time, CSAT, and escalation rates.
