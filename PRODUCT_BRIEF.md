# Agent Guardian — Product Brief (MVP)

| Field | Value |
|-------|-------|
| **Product Name** | Agent Guardian |
| **One-Line** | Real-time AI safety middleware that intercepts, scores, and controls autonomous agent actions before they cause harm. |

## Problem

AI agents (LangChain, AutoGen, CrewAI, OpenAI Agents SDK) can delete files, exfiltrate data, and send emails with no safety layer. One wrong tool call can cause irreversible damage.

## Solution

A Python middleware that wraps any agent tool with `@guardian.watch`, scores every action using **OpenAI gpt-4o-mini**, simulates risky ones with **gpt-4o** judgment, routes approvals via **Slack**, and enables **one-click rollback**.

## How OpenAI Powers It

| Use | Model |
|-----|-------|
| Risk scoring (structured JSON) | gpt-4o-mini |
| Simulation outcome judge | gpt-4o |
| Approval summaries | gpt-4o-mini |

Plus a **rule engine** for instant blocks (`rm -rf`, `curl \| bash`) with zero API latency.

## Demo

- **API:** `http://localhost:8000/health`
- **Dashboard:** `cd dashboard && npm run dev`
- **Install:** `pip install -e .`
- **Scenarios:** `python examples/demo_destroyer.py`

## Metrics (target)

- 0 false negatives on critical-risk actions (rule engine + score ≥95 block)
- &lt;100ms intercept latency for rule-engine hits
- 3 live attack scenarios in demo video

## Links

- GitHub: `github.com/YOUR_HANDLE/agent-guardian`
- Live dashboard: deploy to Vercel with `NEXT_PUBLIC_API_URL`
