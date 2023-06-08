from steamship import File, Steamship, SteamshipError, Tag


def update_file_status(client: Steamship, file: File, status: str) -> None:
    file = file.refresh()
    status_tags = [tag for tag in file.tags if tag.kind == "status"]
    for status_tag in status_tags:
        try:
            status_tag.client = client
            status_tag.delete()
        except SteamshipError:
            pass

    Tag.create(client, file_id=file.id, kind="status", name=status)
