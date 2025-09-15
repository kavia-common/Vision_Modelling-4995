from __future__ import annotations

from datetime import datetime, timezone


# PUBLIC_INTERFACE
def utcnow() -> datetime:
    """Get the current UTC datetime with tzinfo set."""
    return datetime.now(timezone.utc)


# PUBLIC_INTERFACE
def isoformat_utc(dt: datetime) -> str:
    """Return an ISO 8601 string for a datetime, ensuring UTC timezone.

    Args:
        dt (datetime): Datetime to format.

    Returns:
        str: ISO formatted string with UTC 'Z' suffix where possible.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    # Use .isoformat() and normalize 'Z'
    s = dt.isoformat()
    if s.endswith("+00:00"):
        s = s[:-6] + "Z"
    return s
