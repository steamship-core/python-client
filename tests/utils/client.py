from steamship import Steamship


def get_steamship_client() -> Steamship:
    return Steamship(profile="test")
