"""Scenario 1: The Destroyer — rm -rf blocked by Guardian (no real deletion)."""

import asyncio

from agent_guardian import watch


@watch
async def run_shell_command(cmd: str) -> str:
    """Simulates agent executing a shell command (never runs for real in demo)."""
    return f"Would execute: {cmd}"


async def main() -> None:
    print("Running Destroyer scenario...")
    print("Agent tries: rm -rf /home/user/projects\n")
    try:
        await run_shell_command("rm -rf /home/user/projects")
        print("ERROR: action should have been blocked")
    except PermissionError as exc:
        print(f"[Guardian] Blocked: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
