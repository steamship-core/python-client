from steamship import Steamship


def get_steamship_client(**kwargs) -> Steamship:
    # Always use the `test` profile
    kwargs["profile"] = "test"
    return Steamship(**kwargs)
