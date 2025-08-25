# tests/utils.py
import time
from datetime import datetime, timezone

def unique(prefix: str) -> str:
    """
    Return a unique string for use in payloads to avoid collisions.
    Example: unique("Crypto") -> "Crypto_1735145975123"
    """
    return f"{prefix}_{int(time.time() * 1000)}"

def parse_items(body):
    """
    Normalize list responses.
    Some APIs return a bare list, others wrap in {"items": [...], "total": N}.
    This helper extracts the list either way.
    """
    if isinstance(body, dict) and "items" in body:
        return body["items"]
    return body

def iso_utc(dt: datetime) -> str:
    """
    Return RFC3339/ISO-8601 string in UTC, with trailing Z.
    Example: 2025-08-24T12:00:00Z
    """
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def now_plus(minutes: int = 0, hours: int = 0, days: int = 0) -> str:
    """
    Convenience: current UTC time + offset, formatted for API payloads.
    Example: now_plus(hours=1) -> "2025-08-24T13:00:00Z"
    """
    delta = datetime.now(timezone.utc) + timedelta(minutes=minutes, hours=hours, days=days)
    return iso_utc(delta)
