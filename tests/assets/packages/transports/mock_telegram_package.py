from typing import List

from steamship import File, Tag
from steamship.invocable import PackageService, get


class MockTelegram(PackageService):
    WEBHOOK_TAG = "webhook"

    @get("setWebhook", public=True)
    def set_webhook(self, url: str, allowed_updates: List[str], drop_pending_updates: bool):
        File.create(self.client, blocks=[], tags=[Tag(kind=self.WEBHOOK_TAG, name=url)])
