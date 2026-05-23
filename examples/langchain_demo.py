"""Wrap any LangChain tool with @guardian.watch."""

import asyncio

from agent_guardian import watch


@watch
async def search_web(query: str) -> str:
    return f"Results for: {query}"


@watch
async def write_file(path: str, content: str) -> str:
    return f"Wrote {len(content)} bytes to {path}"


async def main() -> None:
    print(await search_web("agent safety best practices"))
    try:
        await write_file("/tmp/notes.txt", "hello")
        print("File write allowed")
    except PermissionError as exc:
        print(f"Blocked: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
