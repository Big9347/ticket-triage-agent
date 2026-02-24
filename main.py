"""
Entry point for the Support Ticket Triage Agent.

Loads environment variables, processes all sample tickets,
and displays rich-formatted triage results in the terminal.
"""

from __future__ import annotations

import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from agent import triage_ticket
from data import SAMPLE_TICKETS
from models import UrgencyLevel, NextAction


# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------

URGENCY_STYLES = {
    UrgencyLevel.CRITICAL: ("bold white on red", "🔴 CRITICAL"),
    UrgencyLevel.HIGH:     ("bold white on dark_orange3", "🟠 HIGH"),
    UrgencyLevel.MEDIUM:   ("bold black on yellow", "🟡 MEDIUM"),
    UrgencyLevel.LOW:      ("bold white on green", "🟢 LOW"),
}

ACTION_LABELS = {
    NextAction.AUTO_RESPOND:    "💬 Auto-Respond",
    NextAction.ROUTE_SPECIALIST: "🔀 Route to Specialist",
    NextAction.ESCALATE_HUMAN:  "🚨 Escalate to Human",
}


def display_result(console: Console, result, ticket) -> None:
    """Pretty-print a single triage result."""
    style, badge = URGENCY_STYLES.get(
        result.urgency_level, ("", str(result.urgency_level))
    )

    # Header
    header = Text()
    header.append(f" {badge} ", style=style)
    header.append(f"  Score: {result.urgency_score}/100", style="bold")

    console.print()
    console.print(Panel(
        header,
        title=f"[bold cyan]Ticket {result.ticket_id}[/bold cyan] — {ticket.subject}",
        border_style="cyan",
        padding=(0, 1),
    ))

    # Score breakdown table
    sb = result.score_breakdown
    score_table = Table(
        title="Score Breakdown",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold magenta",
    )
    score_table.add_column("Component", style="dim")
    score_table.add_column("Score", justify="right")
    score_table.add_column("Max", justify="right", style="dim")
    score_table.add_row("Customer Value", str(sb.customer_value), "20")
    score_table.add_row("Impact", str(sb.impact), "20")
    score_table.add_row("Urgency Signals", str(sb.urgency_signals), "20")
    score_table.add_row("Repeat Issue", str(sb.repeat_issue), "20")
    score_table.add_row("Outage Boost", str(sb.outage_boost), "20")
    score_table.add_row(
        "[bold]Total[/bold]",
        f"[bold]{result.urgency_score}[/bold]",
        "[bold]100[/bold]",
    )
    console.print(score_table)

    # Extracted info
    info = result.extracted_info
    info_table = Table(
        title="Extracted Information",
        box=box.SIMPLE_HEAVY,
        show_header=False,
    )
    info_table.add_column("Field", style="bold")
    info_table.add_column("Value")
    info_table.add_row("Product Area", info.product_area)
    info_table.add_row("Issue Type", info.issue_type)
    info_table.add_row("Sentiment", info.sentiment.value)
    info_table.add_row("Language", info.language)
    info_table.add_row("Summary", info.summary)
    console.print(info_table)

    # Action & routing
    action_label = ACTION_LABELS.get(result.next_action, str(result.next_action))
    console.print(f"  [bold]Action:[/bold]  {action_label}")
    console.print(f"  [bold]Queue:[/bold]   {result.routing_queue}")

    # Reasoning
    console.print(Panel(
        result.reasoning,
        title="[bold yellow]Reasoning[/bold yellow]",
        border_style="yellow",
        padding=(0, 1),
    ))

    # Suggested response
    console.print(Panel(
        result.suggested_response,
        title="[bold green]Suggested Response[/bold green]",
        border_style="green",
        padding=(0, 1),
    ))

    # KB articles used
    if result.knowledge_articles_used:
        console.print(
            f"  [dim]KB Articles Referenced: {', '.join(result.knowledge_articles_used)}[/dim]"
        )

    console.print("─" * 80)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    load_dotenv()
    console = Console()

    console.print()
    console.print(
        Panel(
            "[bold white]Support Ticket Triage Agent[/bold white]\n"
            "[dim]Powered by OpenAI GPT + Pydantic structured output[/dim]",
            border_style="bright_blue",
            padding=(1, 2),
        )
    )

    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    for i, ticket in enumerate(SAMPLE_TICKETS, start=1):
        console.print(
            f"\n[bold blue]Processing ticket {i}/{len(SAMPLE_TICKETS)}:[/bold blue] "
            f"{ticket.ticket_id} — {ticket.subject}"
        )
        if verbose:
            console.print("[dim]  (verbose mode — showing tool calls)[/dim]")

        try:
            result = triage_ticket(ticket, verbose=verbose)
            display_result(console, result, ticket)
        except Exception as exc:
            console.print(f"[bold red]  ✗ Error processing {ticket.ticket_id}: {exc}[/bold red]")

    console.print("\n[bold green]✓ All tickets processed.[/bold green]\n")


if __name__ == "__main__":
    main()
