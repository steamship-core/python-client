import os


def is_in_replit() -> bool:
    """Returns True if the user appears to be inside Replit."""
    if os.environ.get("REPLIT_CLI") or os.environ.get("REPLIT_DB_URL"):
        return True

    return False
