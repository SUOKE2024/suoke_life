"""Time utilities for look service."""

from datetime import UTC, datetime


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format.

    Returns:
        ISO formatted timestamp string
    """
    return datetime.now(UTC).isoformat()


def format_timestamp(
    timestamp: datetime | None = None,
    format_str: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """Format timestamp to string.

    Args:
        timestamp: Datetime object (defaults to current time)
        format_str: Format string

    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now(UTC)

    return timestamp.strftime(format_str)


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse timestamp string to datetime object.

    Args:
        timestamp_str: ISO formatted timestamp string

    Returns:
        Datetime object

    Raises:
        ValueError: If timestamp format is invalid
    """
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}") from e


def timestamp_to_unix(timestamp: datetime) -> int:
    """Convert datetime to unix timestamp.

    Args:
        timestamp: Datetime object

    Returns:
        Unix timestamp (seconds since epoch)
    """
    return int(timestamp.timestamp())


def unix_to_timestamp(unix_time: int) -> datetime:
    """Convert unix timestamp to datetime.

    Args:
        unix_time: Unix timestamp

    Returns:
        Datetime object
    """
    return datetime.fromtimestamp(unix_time, tz=UTC)
