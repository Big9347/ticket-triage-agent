"""
Mock data layer for the Support Ticket Triage Agent.

Contains sample tickets (from homework), customer database,
and knowledge base articles — all as Pydantic model instances.
"""

from models import (
    CustomerHistory,
    KnowledgeBaseArticle,
    Ticket,
    TicketMessage,
)


# ---------------------------------------------------------------------------
# Mock customer database
# ---------------------------------------------------------------------------

CUSTOMERS: dict[str, CustomerHistory] = {
    "cust_001": CustomerHistory(
        customer_id="cust_001",
        name="Alex Rivera",
        email="alex.r@example.com",
        plan="free",
        mrr=0.0,
        tenure_months=4,
        seats=1,
        usage_last_7d=5,
        usage_last_30d=18,
        total_tickets=0,
        open_tickets=1,
        last_csat_score=None,
        previous_escalations=0,
        active_incidents=[],
    ),
    "cust_002": CustomerHistory(
        customer_id="cust_002",
        name="Somchai Thanaporn",
        email="somchai.t@enterprise-th.example.com",
        plan="enterprise",
        mrr=4500.0,
        tenure_months=8,
        seats=45,
        usage_last_7d=7,
        usage_last_30d=30,
        total_tickets=3,
        open_tickets=1,
        last_csat_score=4.2,
        previous_escalations=0,
        active_incidents=["INC-2024-0892: Intermittent 500 errors in Asia-Pacific region"],
    ),
    "cust_003": CustomerHistory(
        customer_id="cust_003",
        name="Jordan Patel",
        email="jordan.p@example.com",
        plan="pro",
        mrr=29.99,
        tenure_months=5,
        seats=1,
        usage_last_7d=7,
        usage_last_30d=28,
        total_tickets=0,
        open_tickets=1,
        last_csat_score=None,
        previous_escalations=0,
        active_incidents=[],
    ),
}


# ---------------------------------------------------------------------------
# Mock knowledge base
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE: list[KnowledgeBaseArticle] = [
    KnowledgeBaseArticle(
        article_id="KB-001",
        title="Troubleshooting Failed Payment & Duplicate Charges",
        content=(
            "If a customer experiences a failed payment during plan upgrade, "
            "check the payment gateway logs for declined transactions. Duplicate "
            "pending charges typically resolve within 3-5 business days as "
            "authorisation holds expire. If the customer needs immediate resolution: "
            "1) Verify charges in Stripe dashboard, 2) Void any duplicate authorisations, "
            "3) Manually activate the plan upgrade, 4) Confirm with the customer."
        ),
        tags=["billing", "payment", "upgrade", "charges", "duplicate", "refund"],
        category="Billing",
    ),
    KnowledgeBaseArticle(
        article_id="KB-002",
        title="How to Upgrade from Free to Pro Plan",
        content=(
            "Navigate to Settings > Subscription > Upgrade. Select the Pro plan "
            "and enter payment details. The upgrade is effective immediately. "
            "Pro features include: advanced exports (PDF, PPTX), priority support, "
            "custom branding, and API access."
        ),
        tags=["billing", "upgrade", "pro", "plan", "subscription"],
        category="Billing",
    ),
    KnowledgeBaseArticle(
        article_id="KB-003",
        title="Resolving HTTP 500 Internal Server Errors",
        content=(
            "HTTP 500 errors indicate a server-side issue. Steps to diagnose: "
            "1) Check status.company.com for active incidents, "
            "2) Verify if the issue is region-specific (check regional health dashboard), "
            "3) Ask the customer for their region/data-centre, "
            "4) Check recent deployment logs for regressions. "
            "For enterprise customers, escalate to the on-call SRE immediately "
            "if the issue persists beyond 30 minutes."
        ),
        tags=["error", "500", "outage", "server", "region", "enterprise"],
        category="Technical",
    ),
    KnowledgeBaseArticle(
        article_id="KB-004",
        title="Regional Infrastructure & Data Centres",
        content=(
            "We operate in 4 regions: US-East, US-West, EU-West, and Asia-Pacific. "
            "Enterprise customers in Thailand are routed through the Asia-Pacific region "
            "(ap-southeast-1). Regional outages should be verified via the internal "
            "region health dashboard at internal.company.com/health."
        ),
        tags=["region", "infrastructure", "asia", "enterprise", "data centre"],
        category="Technical",
    ),
    KnowledgeBaseArticle(
        article_id="KB-005",
        title="Dark Mode & Appearance Settings",
        content=(
            "Dark mode is available under Settings > Appearance. Users can choose "
            "'Light', 'Dark', or 'System Default'. Known issue: the 'System Default' "
            "option on macOS may not correctly detect dark mode if the app was opened "
            "before the system theme was changed. Workaround: restart the app after "
            "changing macOS appearance settings. A fix is planned for v2.14."
        ),
        tags=["dark mode", "appearance", "theme", "settings", "ui", "bug"],
        category="Product",
    ),
    KnowledgeBaseArticle(
        article_id="KB-006",
        title="Feature Requests & Feedback Process",
        content=(
            "We track feature requests in our public roadmap at roadmap.company.com. "
            "To submit on behalf of a customer: 1) Log the request in the feedback tool, "
            "2) Tag the customer's plan tier, 3) Link to the support ticket. "
            "Scheduled/automated dark mode is on the roadmap for Q3. "
            "Pro and Enterprise customer requests are prioritised."
        ),
        tags=["feature request", "feedback", "roadmap", "dark mode", "schedule"],
        category="Product",
    ),
    KnowledgeBaseArticle(
        article_id="KB-007",
        title="Escalation Policy & SLA Guidelines",
        content=(
            "Critical tickets (score 60+) must be acknowledged within 15 minutes. "
            "Enterprise customers with active incidents get automatic escalation to "
            "the on-call engineering team. High-priority tickets (score 40-59) should "
            "be responded to within 1 hour. Medium and low tickets follow standard SLA "
            "of 4 hours and 24 hours respectively."
        ),
        tags=["escalation", "sla", "priority", "enterprise", "critical"],
        category="Process",
    ),
]


# ---------------------------------------------------------------------------
# Sample tickets
# ---------------------------------------------------------------------------

SAMPLE_TICKETS: list[Ticket] = [
    # Ticket 1 — Billing / duplicate charges (Free plan user)
    Ticket(
        ticket_id="TKT-1001",
        customer_id="cust_001",
        channel="email",
        subject="Payment failed during Pro upgrade — duplicate charges",
        messages=[
            TicketMessage(
                body="My payment failed when I tried to upgrade to Pro. Can you check what's wrong?",
                timestamp="3 hours ago",
            ),
            TicketMessage(
                body="I tried again with a different card. Now I see TWO pending charges but my account still shows Free plan??",
                timestamp="2 hours ago",
            ),
            TicketMessage(
                body=(
                    "Okay this is getting ridiculous. Just checked my bank app - "
                    "I have THREE charges of $29.99 now. None of them refunded. "
                    "And I STILL don't have Pro access."
                ),
                timestamp="1 hour ago",
            ),
            TicketMessage(
                body=(
                    "HELLO?? Is anyone there??? I need this fixed NOW. I have a "
                    "presentation in 2 hours and I need the Pro export features. "
                    "If these charges aren't reversed by end of day I'm disputing "
                    "all of them with my bank."
                ),
                timestamp="just now",
            ),
        ],
        tags=["billing", "payment", "upgrade"],
    ),
    # Ticket 2 — Enterprise outage in Thailand (Thai language)
    Ticket(
        ticket_id="TKT-1002",
        customer_id="cust_002",
        channel="email",
        subject="System down — Error 500 across all browsers",
        messages=[
            TicketMessage(
                body=(
                    "ระบบเข้าไม่ได้ครับ ขึ้น error 500\n"
                    "(Can't access the system, showing error 500)"
                ),
                timestamp="2 hours ago",
            ),
            TicketMessage(
                body=(
                    "ลองหลายเครื่องแล้ว ทั้ง Chrome, Safari, Firefox ผลเหมือนกันหมด "
                    "เพื่อนร่วมงานก็เข้าไม่ได้เหมือนกัน\n"
                    "(Tried multiple machines — Chrome, Safari, Firefox — same result. "
                    "Coworkers also can't access)"
                ),
                timestamp="1.5 hours ago",
            ),
            TicketMessage(
                body=(
                    "ตอนนี้ลูกค้าโวยเข้ามาเยอะมาก เรามี demo กับลูกค้ารายใหญ่บ่ายนี้ "
                    "ถ้าระบบไม่กลับมา deal นี้อาจจะหลุด\n"
                    "(Customers are flooding in with complaints now. We have a demo with "
                    "a major client this afternoon. If the system doesn't come back, "
                    "we might lose this deal)"
                ),
                timestamp="45 mins ago",
            ),
            TicketMessage(
                body=(
                    "เช็ค status.company.com แล้ว บอกว่า all systems operational "
                    "แต่เราใช้งานไม่ได้จริงๆ ช่วยเช็คให้หน่อยได้ไหมครับ "
                    "region Asia มีปัญหาหรือเปล่า?\n"
                    "(Checked status.company.com — it says all systems operational, "
                    "but we really can't use it. Can you please check? "
                    "Is there an issue with the Asia region?)"
                ),
                timestamp="just now",
            ),
        ],
        tags=["outage", "error", "enterprise", "asia"],
    ),
    # Ticket 3 — Dark mode feature request / bug (Pro user)
    Ticket(
        ticket_id="TKT-1003",
        customer_id="cust_003",
        channel="email",
        subject="Dark mode not working / feature request",
        messages=[
            TicketMessage(
                body="Hey, just wondering if you support dark mode? No rush 😊",
                timestamp="2 days ago",
            ),
            TicketMessage(
                body=(
                    "Thanks for the reply! Oh nice, so it's in Settings > Appearance. "
                    "Found it! But hmm I'm on Pro plan and I only see 'Light' and "
                    "'System Default' options. No dark mode toggle?"
                ),
                timestamp="1 day ago",
            ),
            TicketMessage(
                body=(
                    "Okay so I switched to 'System Default' and my Mac is set to "
                    "dark mode, but your app still shows light theme. Is this a bug "
                    "or am I missing something?"
                ),
                timestamp="1 day ago (3 hours later)",
            ),
            TicketMessage(
                body=(
                    "Also random question while I have you — is there a way to schedule "
                    "dark mode? Like auto-switch at 6pm? Some apps have that. Would be "
                    "cool if you guys added it 👀"
                ),
                timestamp="today",
            ),
        ],
        tags=["dark mode", "feature request", "ui", "bug"],
    ),
]
