def remove_none(d: dict) -> dict:
    """Removes all the None values in a dict, returning a copy of the dict."""
    return {k: v for k, v in d.items() if v is not None}
