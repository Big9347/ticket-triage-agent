"""
Tool definitions for the Support Ticket Triage Agent.

Each tool has:
  - An OpenAI function-calling schema (for the `tools` parameter)
  - A Python implementation that returns JSON-serializable data

Tools:
  1. lookup_customer_history — retrieve enriched customer context
  2. search_knowledge_base  — search FAQ / docs by keyword query
"""

from __future__ import annotations

import json

from data import CUSTOMERS, KNOWLEDGE_BASE


# =========================================================================
# Tool 1: Lookup Customer History
# =========================================================================

LOOKUP_CUSTOMER_HISTORY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "lookup_customer_history",
        "description": (
            "Look up a customer's full context including plan, MRR, usage stats, "
            "past support history, CSAT scores, escalation history, and any "
            "active incidents. Use this to understand customer value and context "
            "before scoring urgency."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The unique customer identifier, e.g. 'cust_001'",
                },
            },
            "required": ["customer_id"],
            "additionalProperties": False,
        },
    },
}


def _strip_empty(d: dict) -> dict:
    """Remove keys whose values are None, empty strings, or empty lists."""
    return {k: v for k, v in d.items() if v is not None and v != "" and v != []}


def lookup_customer_history(customer_id: str) -> dict:
    """Return customer context as a dictionary, or an error message."""
    customer = CUSTOMERS.get(customer_id)
    if customer is None:
        return {"error": f"Customer '{customer_id}' not found in database."}
    return _strip_empty(customer.model_dump())


# =========================================================================
# Tool 2: Search Knowledge Base
# =========================================================================

SEARCH_KNOWLEDGE_BASE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": (
            "Search the internal knowledge base (FAQ & docs) for articles relevant "
            "to a customer's issue. Returns matching articles ranked by relevance. "
            "Use this to find solutions, workarounds, or relevant documentation "
            "before composing a response."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Search query describing the issue, e.g. "
                        "'payment failed duplicate charges' or 'error 500 asia region'"
                    ),
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}


def search_knowledge_base(query: str) -> list[dict]:
    """
    Simple keyword-overlap search over the knowledge base.
    Returns articles sorted by relevance score (descending).
    """
    query_tokens = set(query.lower().split())
    scored: list[tuple[float, dict]] = []

    for article in KNOWLEDGE_BASE:
        # Build a set of tokens from title, tags, and content
        article_tokens = set()
        article_tokens.update(article.title.lower().split())
        article_tokens.update(article.content.lower().split())
        for tag in article.tags:
            article_tokens.update(tag.lower().split())

        overlap = query_tokens & article_tokens
        if overlap:
            score = len(overlap) / len(query_tokens)
            scored.append((score, article.model_dump()))

    # Sort by score descending, return top 3
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:3]]


# =========================================================================
# Registry — maps function name → callable
# =========================================================================

TOOL_SCHEMAS = [
    LOOKUP_CUSTOMER_HISTORY_SCHEMA,
    SEARCH_KNOWLEDGE_BASE_SCHEMA,
]

TOOL_FUNCTIONS: dict[str, callable] = {
    "lookup_customer_history": lookup_customer_history,
    "search_knowledge_base": search_knowledge_base,
}


def execute_tool(name: str, arguments: str) -> str:
    """Execute a tool by name with JSON-encoded arguments. Returns JSON string."""
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        args = json.loads(arguments)
        
        # Handle common LLM hallucination where it nests args inside "parameters"
        if "parameters" in args and "query" not in args:
            args = args["parameters"]
            
        result = func(**args)
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        # Feed the error back to the LLM so it can try again
        return json.dumps({
            "error": f"Tool execution failed: {type(e).__name__}: {str(e)}. Please correct your arguments and try again."
        })
