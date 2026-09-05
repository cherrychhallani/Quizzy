from datetime import datetime, timezone


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def seconds_elapsed(started_at: str) -> int:
    started = parse_iso(started_at)
    now = datetime.now(timezone.utc)
    return int((now - started).total_seconds())


def is_within_time_limit(started_at: str, time_limit_seconds: int) -> bool:
    return seconds_elapsed(started_at) <= time_limit_seconds