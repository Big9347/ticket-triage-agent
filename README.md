# Support Ticket Triage Agent

An AI-powered agent that automatically triages incoming customer support tickets using OpenAI's GPT models, Pydantic structured outputs, and function-calling tools.

## Features

- **Urgency Classification** — Weighted scoring system (0–100) that classifies tickets as critical / high / medium / low
- **Information Extraction** — Detects product area, issue type, customer sentiment, and language
- **Knowledge Base Search** — Searches internal FAQ/docs to find relevant solutions
- **Customer Context** — Looks up customer plan, MRR, usage, and support history
- **Intelligent Routing** — Decides whether to auto-respond, route to a specialist, or escalate to a human
- **Multilingual** — Handles tickets in non-English languages (e.g., Thai)
- **Explainable Scoring** — Shows sub-score breakdown so support teams can trust the output

## Project Structure

```
ticket-triage-agent/
├── models.py          # Pydantic models (Ticket, CustomerHistory, TriageResult, etc.)
├── data.py            # Mock data: sample tickets, customer DB, knowledge base
├── tools.py           # Tool definitions for OpenAI function calling
├── agent.py           # Core AI agent with system prompt + tool-call loop
├── main.py            # Entry point — processes sample tickets with rich output
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
├── ARCHITECTURE.md    # Architecture decisions & write-up
└── README.md          # This file
```

## Setup

### Prerequisites

- Python 3.10+
- An OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ticket-triage-agent.git
   cd ticket-triage-agent
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # macOS/Linux
   .venv\Scripts\activate           # Windows
   pip install -r requirements.txt
   ```

3. Set up your API key:
   ```bash
   cp .env.example .env
   # Edit .env and replace 'your-api-key-here' with your actual OpenAI API key
   ```

## Usage

### Basic Run

```bash
python main.py
```

This processes all 3 sample tickets (data.py) and displays triage results in the terminal.

### Verbose Mode

```bash
python main.py --verbose
```

Shows tool calls and responses as the agent processes each ticket.

### Configuration

Set these in your `.env` file:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-5-nano` | Model to use |

## Sample Tickets

The agent comes with 3 sample tickets from a realistic support scenario:

| # | Scenario | Expected Urgency |
|---|---|---|
| 1 | Billing — duplicate charges during plan upgrade, escalating frustration | **High / Critical** |
| 2 | Enterprise outage — Error 500 in Asia region, 45 seats affected, demo at risk (Thai language) | **Critical** |
| 3 | Dark mode not working + feature request, friendly tone | **Low / Medium** |

## Technology Stack

- **[OpenAI Python SDK](https://github.com/openai/openai-python)** — Chat completions with function calling
- **[Pydantic](https://docs.pydantic.dev/)** — Structured data validation and serialisation
- **[Rich](https://rich.readthedocs.io/)** — Beautiful terminal output
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — Environment variable management
