from datetime import datetime, timezone

def now() -> datetime:
    """Return the current time in UTC with tzinfo."""
    return datetime.now(timezone.utc)
