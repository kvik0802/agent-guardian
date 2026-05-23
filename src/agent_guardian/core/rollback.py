"""Snapshot and rollback — Redis-backed with in-memory fallback."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_guardian.config import settings

_memory_snaps: dict[str, str] = {}
_memory_approvals: dict[str, str] = {}


async def _redis_get(key: str) -> str | None:
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        val = await r.get(key)
        await r.aclose()
        return val.decode() if val else None
    except Exception:
        return _memory_snaps.get(key)


async def _redis_set(key: str, value: str, ex: int = 86400) -> None:
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        await r.set(key, value, ex=ex)
        await r.aclose()
    except Exception:
        _memory_snaps[key] = value


async def set_approval(action_id: str, decision: str) -> None:
    """Store approve/deny decision."""
    key = f"approval:{action_id}"
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        await r.set(key, decision, ex=600)
        await r.aclose()
    except Exception:
        _memory_approvals[key] = decision


async def get_approval(action_id: str) -> str | None:
    key = f"approval:{action_id}"
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        val = await r.get(key)
        await r.aclose()
        return val.decode() if val else None
    except Exception:
        return _memory_approvals.get(key)


async def snapshot_state(base_dir: str = ".", max_files: int = 50) -> str:
    """Capture file tree snapshot. Returns snapshot_id."""
    snap_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    tree: dict[str, str | None] = {}
    count = 0
    for p in Path(base_dir).rglob("*"):
        if count >= max_files:
            break
        if not p.is_file() or ".git" in str(p) or "node_modules" in str(p):
            continue
        try:
            if p.stat().st_size > 100_000:
                continue
            tree[str(p)] = p.read_text(errors="replace")
            count += 1
        except OSError:
            tree[str(p)] = None

    snap: dict[str, Any] = {
        "id": snap_id,
        "tree": tree,
        "env_keys": list(os.environ.keys()),
    }
    await _redis_set(f"snap:{snap_id}", json.dumps(snap))
    return snap_id


async def rollback(snap_id: str) -> bool:
    """Restore files from snapshot."""
    raw = await _redis_get(f"snap:{snap_id}")
    if not raw:
        return False
    snap = json.loads(raw)
    tree = snap.get("tree", {})
    for path, content in tree.items():
        if content is not None:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    return True


async def cascade_rollback(action_ids: list[str]) -> dict[str, bool]:
    """Rollback multiple snapshots in reverse order."""
    results: dict[str, bool] = {}
    for aid in reversed(action_ids):
        results[aid] = await rollback(aid)
    return results
