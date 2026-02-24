"""
AI Agent for Support Ticket Triage.

Uses the OpenAI Chat Completions API with function calling to:
  1. Classify ticket urgency (critical / high / medium / low)
  2. Extract key information (product area, issue type, sentiment)
  3. Search the knowledge base for relevant articles
  4. Decide next action (auto-respond, route to specialist, escalate)
"""

from __future__ import annotations

import json
import os
from typing import Optional

from openai import OpenAI, APIError
from pydantic import ValidationError

from models import Ticket, TriageResult
from tools import TOOL_SCHEMAS, execute_tool


# ---------------------------------------------------------------------------
# System prompt — drives the agent's behaviour
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert Support Ticket Triage Agent. Your job is to analyse incoming \
customer support tickets and produce a structured triage decision.

## Your Workflow

1. **Read the ticket** carefully — all messages in the thread, noting escalating \
   frustration, time sensitivity, and business impact.
2. **Use the `lookup_customer_history` tool** to retrieve the customer's plan, \
   MRR, usage data, past tickets, CSAT, escalation history, and any active incidents.
3. **Use the `search_knowledge_base` tool** to find relevant FAQ / documentation \
   articles that could help resolve the issue.
4. **Classify urgency** using a weighted scoring system (0-100):
   - Customer value (plan tier + MRR): 0-20 points
   - Impact signals (what broke, how many affected, revenue at risk): 0-20 points. 
     *(Note: Cosmetic bugs or feature requests MUST score 0-5 points)*
   - Urgency signals (language intensity, deadlines mentioned): 0-20 points.
     *(Note: Polite feature requests or "no rush" comments MUST score 0 points)*
   - Repeat issue (same problem reported recently): 0-20 points
   - Outage boost (active incident affecting this customer): 0-20 points

   Urgency buckets:
   - **critical**: score >= 60
   - **high**: score 40-59
   - **medium**: score 20-39
   - **low**: score < 20

5. **Extract key information**: product area, issue type, customer sentiment, \
   language, and a one-line summary.
6. **Decide next action**:
   - `auto_respond` — issue can be resolved with KB article / known workaround
   - `route_specialist` — needs domain expertise (billing, engineering, product)
   - `escalate_human` — high-value / critical issue needing human judgement

7. **Draft a suggested response** to the customer — empathetic, specific, and \
   actionable. Match the customer's language when possible.

## Output Format

You MUST respond with a single JSON object matching this exact schema (no markdown, \
no extra text, ONLY the JSON):

{
  "ticket_id": "<string>",
  "urgency_level": "critical|high|medium|low",
  "urgency_score": <int 0-100>,
  "score_breakdown": {
    "customer_value": <int 0-20>,
    "impact": <int 0-20>,
    "urgency_signals": <int 0-20>,
    "repeat_issue": <int 0-20>,
    "outage_boost": <int 0-20>
  },
  "extracted_info": {
    "product_area": "<string>",
    "issue_type": "<string>",
    "sentiment": "frustrated|angry|neutral|positive|anxious",
    "language": "<ISO 639-1 code>",
    "summary": "<one-line summary>"
  },
  "next_action": "auto_respond|route_specialist|escalate_human",
  "routing_queue": "<team/queue name>",
  "suggested_response": "<draft response to customer>",
  "reasoning": "<brief explanation of triage decision>",
  "knowledge_articles_used": ["<article_id>", ...]
}

## Important Rules

- ALWAYS call BOTH tools before making your decision.
- If the ticket is in a non-English language, still extract information correctly \
  and write the suggested_response in the SAME language as the customer.
- Be specific in your reasoning — explain which signals drove the score.
- The suggested_response should acknowledge the customer's frustration if present.
- For billing issues with monetary impact, lean toward escalation.
- For enterprise customers with service outages, always classify as critical.
"""


# ---------------------------------------------------------------------------
# Agent function
# ---------------------------------------------------------------------------

def triage_ticket(
    ticket: Ticket,
    model: Optional[str] = None,
    verbose: bool = False,
) -> TriageResult:
    """
    Run the triage agent on a single ticket.

    Sends the ticket to the LLM with tool definitions, handles tool calls
    in a loop, and parses the final response into a TriageResult.
    """
    client = OpenAI()  # uses OPENAI_API_KEY env var
    model = model or os.getenv("OPENAI_MODEL", "gpt-5-nano-2025-08-07")

    # Build the user message from ticket data
    ticket_payload = ticket.model_dump_json(indent=2)
    user_message = (
        f"Please triage the following support ticket:\n\n"
        f"```json\n{ticket_payload}\n```"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    # Agentic loop — keep calling until we get a final response
    max_iterations = 10
    for iteration in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                temperature=1, # 0.2 for higher models, 1 for gpt-5-nano
            )
        except APIError as e:
            print(f"Error: {e}")
            continue

        choice = response.choices[0]

        # If the model wants to call tools, execute them and feed results back
        if choice.finish_reason == "tool_calls" or choice.message.tool_calls:
            messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = tool_call.function.arguments

                if verbose:
                    print(f"  Tool call: {fn_name}({fn_args})")

                result = execute_tool(fn_name, fn_args)

                if verbose:
                    print(f"  Result: {result[:200]}...")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            continue  # Go back to the model with tool results

        # Final response — parse the JSON
        raw_content = choice.message.content.strip()

        # Strip potential markdown fencing
        if raw_content.startswith("```"):
            lines = raw_content.split("\n")
            # Remove first and last lines (``` markers)
            lines = [l for l in lines if not l.strip().startswith("```")]
            raw_content = "\n".join(lines)

        try:
            triage_data = json.loads(raw_content)
            return TriageResult(**triage_data)
        except (json.JSONDecodeError, ValidationError) as exc:
            if verbose:
                print(f"  Parse error on iteration {iteration}: {exc}")
            # Ask the model to fix the output
            messages.append(choice.message)
            messages.append({
                "role": "user",
                "content": (
                    f"Your response was not valid JSON or did not match the expected schema. "
                    f"Error: {exc}\n\n"
                    f"Please respond with ONLY the corrected JSON object."
                ),
            })
            continue

    raise RuntimeError(
        f"Agent did not produce a valid triage result after {max_iterations} iterations."
    )
