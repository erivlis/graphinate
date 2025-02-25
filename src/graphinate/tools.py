from datetime import datetime, timezone

UTC = timezone.utc


def utcnow() -> datetime:
    return datetime.now(tz=UTC)
