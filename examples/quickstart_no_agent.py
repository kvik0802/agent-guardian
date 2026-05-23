"""
Quickstart — NO separate agent required.

This script *simulates* what an AI agent does: it "decides" to call tools.
Guardian wraps those tools and blocks/approves before they run.

Run:  python examples/quickstart_no_agent.py
  or: python -c "from agent_guardian.demos import run_quickstart; run_quickstart()"
"""

import asyncio

from agent_guardian import watch

# --- These are your "agent tools" (any async functions) ---


@watch
async def list_files(folder: str) -> list[str]:
    return [f"{folder}/readme.txt", f"{folder}/data.csv"]


@watch
async def run_command(cmd: str) -> str:
    return f"Would run: {cmd}"


@watch
async def send_email(to: str, subject: str) -> dict[str, str]:
    return {"to": to, "subject": subject, "status": "sent (mock)"}


async def fake_agent_loop() -> None:
    """Pretend to be an agent: pick a tool + args, Guardian intercepts each call."""
    print("Simulated agent starting...\n")

    print("1) Safe tool — list_files")
    files = await list_files("/tmp")
    print(f"   OK: {files}\n")

    print("2) Dangerous tool — run_command('rm -rf /')")
    try:
        await run_command("rm -rf /home/user/projects")
    except PermissionError as e:
        print(f"   Guardian blocked: {e}\n")

    print("3) Risky tool — send_email (needs approval in dev mode unless auto-approve)")
    try:
        result = await send_email("boss@company.com", "Q4 numbers attached")
        print(f"   OK: {result}\n")
    except PermissionError as e:
        print(f"   Guardian denied: {e}\n")

    print("Done. You did NOT need LangChain/OpenAI Agents — just @watch on functions.")


if __name__ == "__main__":
    asyncio.run(fake_agent_loop())
