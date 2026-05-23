"""CLI entry: uvicorn agent_guardian.api.main:app"""


def main() -> None:
    import uvicorn

    uvicorn.run("agent_guardian.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
