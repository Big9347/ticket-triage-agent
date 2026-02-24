"""
Pydantic models for the Support Ticket Triage Agent.

Defines structured schemas for tickets, customer context,
knowledge base articles, and triage results.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UrgencyLevel(str, Enum):
    """Ticket urgency classification."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NextAction(str, Enum):
    """Recommended next action for a triaged ticket."""
    AUTO_RESPOND = "auto_respond"
    ROUTE_SPECIALIST = "route_specialist"
    ESCALATE_HUMAN = "escalate_human"


class Sentiment(str, Enum):
    """Customer sentiment detected in the ticket."""
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    ANXIOUS = "anxious"


# ---------------------------------------------------------------------------
# Ticket models
# ---------------------------------------------------------------------------

class TicketMessage(BaseModel):
    """A single message in a support ticket thread."""
    body: str = Field(..., description="The message content")
    timestamp: str = Field(..., description="Relative or absolute timestamp")


class Ticket(BaseModel):
    """An incoming customer support ticket with full thread."""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    customer_id: str = Field(..., description="Customer identifier")
    channel: str = Field(default="email", description="Support channel")
    subject: str = Field(default="", description="Ticket subject line")
    messages: list[TicketMessage] = Field(
        default_factory=list,
        description="Ordered list of messages in the thread",
    )
    tags: list[str] = Field(default_factory=list, description="Tags attached to ticker")


# ---------------------------------------------------------------------------
# Customer context
# ---------------------------------------------------------------------------

class CustomerHistory(BaseModel):
    """Enriched customer context from CRM / billing / usage systems."""
    customer_id: str
    name: str = ""
    email: str = ""
    plan: str = Field(..., description="Current plan: free / pro / enterprise")
    mrr: float = Field(default=0.0, description="Monthly recurring revenue (USD)")
    tenure_months: int = Field(default=0, description="How long they've been a customer")
    seats: int = Field(default=1, description="Number of seats / licenses")
    usage_last_7d: int = Field(default=0, description="Active days in last 7 days")
    usage_last_30d: int = Field(default=0, description="Active days in last 30 days")
    total_tickets: int = Field(default=0, description="Lifetime support tickets")
    open_tickets: int = Field(default=0, description="Currently open tickets")
    last_csat_score: Optional[float] = Field(
        default=None, description="Last CSAT score (1-5)"
    )
    previous_escalations: int = Field(default=0, description="Number of past escalations")
    active_incidents: list[str] = Field(
        default_factory=list,
        description="Any ongoing incidents affecting this customer",
    )


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

class KnowledgeBaseArticle(BaseModel):
    """An article from the internal knowledge base / FAQ."""
    article_id: str
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    category: str = ""


# ---------------------------------------------------------------------------
# Triage result (structured output from the agent)
# ---------------------------------------------------------------------------

class UrgencyScoreBreakdown(BaseModel):
    """Explains why a ticket received a particular urgency score."""
    customer_value: int = Field(
        ..., ge=0, le=20, description="Score component from customer tier/MRR (0-20)"
    )
    impact: int = Field(
        ..., ge=0, le=20, description="Score component from issue severity (0-20)"
    )
    urgency_signals: int = Field(
        ..., ge=0, le=20, description="Score component from language / intent (0-20)"
    )
    repeat_issue: int = Field(
        ..., ge=0, le=20, description="Score component from repeat issues (0-20)"
    )
    outage_boost: int = Field(
        ..., ge=0, le=20, description="Score boost from active incident (0-20)"
    )


class ExtractedInfo(BaseModel):
    """Key information extracted from the ticket."""
    product_area: str = Field(..., description="Product area affected (e.g. billing, auth)")
    issue_type: str = Field(..., description="Type of issue (e.g. bug, feature_request)")
    sentiment: Sentiment = Field(..., description="Customer sentiment")
    language: str = Field(default="en", description="Detected language of the ticket")
    summary: str = Field(..., description="One-line summary of the customer's issue")


class TriageResult(BaseModel):
    """The complete triage output produced by the agent."""
    ticket_id: str
    urgency_level: UrgencyLevel
    urgency_score: int = Field(..., ge=0, le=100, description="Numeric priority score 0-100")
    score_breakdown: UrgencyScoreBreakdown
    extracted_info: ExtractedInfo
    next_action: NextAction
    routing_queue: str = Field(
        ..., description="Team/queue to route the ticket to (e.g. billing, engineering)"
    )
    suggested_response: str = Field(
        ..., description="Draft response the agent would send to the customer"
    )
    reasoning: str = Field(
        ..., description="Brief explanation of why this triage decision was made"
    )
    knowledge_articles_used: list[str] = Field(
        default_factory=list,
        description="IDs of KB articles referenced during triage",
    )
