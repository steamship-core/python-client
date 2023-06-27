import logging
from typing import List, Optional

from pydantic import Field

from steamship import Block, Steamship, SteamshipError
from steamship.agents.llms import OpenAI
from steamship.agents.mixins.transports.transport import Transport
from steamship.agents.schema import Agent, AgentContext, EmitFunc, Metadata
from steamship.agents.service.agent_service import AgentService
from steamship.agents.utils import with_llm
from steamship.invocable import Config, InvocableResponse, InvocationContext, post

POST_URL = "https://slack.com/api/chat.postMessage"


class SlackTransportConfig(Config):
    bot_token: str = Field(description="The secret token for your Slack bot")
    api_base: str = Field("https://api.telegram.org/bot", description="The root API for Slcak")


class SlackTransport(Transport):
    """Experimental base class to encapsulate a Slack communication channel.

     Instructions for using this Bot.

     First, create a bot in Slack:

     1. Create a new Slack App: https://api.slack.com/apps
     2. Create a Bot Token for your Slack App
         1. Add the following token scopes:
             - app_mentions:read (View messages that directly mention the bot)
             - chat:write (Send messages)
         2. Click on "Install to Workplace"
     3. You should now see "Bot User OAuth Token" in your Slack management UI.
        Copy it to a secure place; you'll use it soon.

    Next, add your bot to a channel:

     1. Invite the bot to a channel in your slack by at-mentioning it (it should now show up in the autocomplete list)
        and then clicking "Add to Channel" after the mention.

    Enable Event Subscriptions:

    1. Enable Events
       - Subscribe to app_mention




    """

    api_root: str
    bot_token: str
    agent: Agent
    agent_service: AgentService

    def __init__(
        self,
        client: Steamship,
        config: SlackTransportConfig,
        agent_service: AgentService,
        agent: Agent,
    ):
        super().__init__(client=client)
        self.api_root = f"{config.api_base}{config.bot_token}"
        self.bot_token = config.bot_token
        self.agent = agent
        self.agent_service = agent_service

    def instance_init(self, config: Config, invocation_context: InvocationContext):
        pass

    def _manifest(self) -> dict:
        """Return the Slack Manifest for this Transport."""
        return {
            "display_information": {
                "name": self.agent_service.context.invocable_instance_handle,
                "description": f"An instance of {self.agent_service.context.invocable_handle} powered by Steamship",
            },
            "features": {
                "bot_user": {
                    "display_name": self.agent_service.context.invocable_instance_handle,
                    "always_online": True,
                }
            },
            "oauth_config": {
                "scopes": {
                    "bot": ["commands", "app_mentions:read", "chat:write", "chat:write.public"]
                }
            },
            "settings": {
                "org_deploy_enabled": True,
                "socket_mode_enabled": False,
                "token_rotation_enabled": False,
                "interactivity": {
                    "is_enabled": True,
                    "request_url": f"{self.agent_service.context.invocable_url}slack_respond",
                },
            },
            "event_subscriptions": {"bot_events": ["app_home_opened"]},
        }

    def _manifest_url(self) -> str:
        """Return the Manifest Installation URL of the Bot."""

    def _to_url(self, Block) -> str:
        pass

    def _send(self, blocks: [Block], metadata: Metadata):
        """Send a response to the Slack chat.

        Slack uses the `text` field for fallback.
        But we want to also provide the blocks and attachments for multiple messages that are multi-modal
        """

        text = None
        blocks = None
        chat_id = None

        for block in blocks:
            if blocks is None:
                blocks = []

            if block.chat_id:
                chat_id = block.chat_id

            if block.is_text() or block.text:
                if not text:
                    # This is the fallback for mobile notifications
                    block.text = block.text
                # The real thing we send is a block
                if blocks is None:
                    blocks = []
                blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
            elif block.is_image():
                blocks.append({"type": "image", "image_url": self._to_url(block)})
            elif block.is_audio():
                blocks.append(
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Audio Link"},
                        "url": self._to_url(block),
                    }
                )
            elif block.is_video():
                blocks.append({"type": "video", "video_url": self._to_url(block)})
            else:
                logging.error(
                    f"Slack transport unable to send a block of MimeType {block.mime_type}"
                )

    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        """Parses an inbound Telegram message."""

        chat = payload.get("chat")
        if chat is None:
            raise SteamshipError(f"No `chat` found in Telegram message: {payload}")

        chat_id = chat.get("id")
        if chat_id is None:
            raise SteamshipError(f"No 'chat_id' found in Telegram message: {payload}")

        if not isinstance(chat_id, int):
            raise SteamshipError(
                f"Bad 'chat_id' found in Telegram message: ({chat_id}). Should have been an int."
            )

        message_id = payload.get("message_id")
        if message_id is None:
            raise SteamshipError(f"No 'message_id' found in Telegram message: {payload}")

        if not isinstance(message_id, int):
            raise SteamshipError(
                f"Bad 'message_id' found in Telegram message: ({message_id}). Should have been an int"
            )

        if video_or_voice := (payload.get("voice") or payload.get("video_note")):
            file_id = video_or_voice.get("file_id")
            file_url = self._get_file_url(file_id)
            block = Block(
                text=payload.get("text"),
                url=file_url,
            )
            block.set_chat_id(str(chat_id))
            block.set_message_id(str(message_id))
            return block

        # Some incoming messages (like the group join message) don't have message text.
        # Rather than throw an error, we just don't return a Block.
        message_text = payload.get("text")
        if message_text is not None:
            result = Block(text=message_text)
            result.set_chat_id(str(chat_id))
            result.set_message_id(str(message_id))
            return result
        else:
            return None

    def build_emit_func(self, chat_id: str) -> EmitFunc:
        def new_emit_func(blocks: List[Block], metadata: Metadata):
            for block in blocks:
                block.set_chat_id(chat_id)
            return self.send(blocks, metadata)

        return new_emit_func

    @post("slack_respond", public=True)
    def slack_respond(self, **kwargs) -> InvocableResponse[str]:
        """Endpoint implementing the Slack Bot WebHook contract. This is a PUBLIC endpoint since Slack cannot pass a Bearer token.

        Expects a JSON body of:

        { event: { type } }
        """

        event = kwargs.get("event", {})
        event_type = event.get("type", "unknown")
        event_text = event.get("text", "")
        # Make call to chat.postMessage using bot's token

        chat_id = message.get("chat", {}).get("id")
        try:
            incoming_message = self.parse_inbound(message)
            if incoming_message is not None:
                context = AgentContext.get_or_create(self.client, context_keys={"chat_id": chat_id})
                context.chat_history.append_user_message(
                    text=incoming_message.text, tags=incoming_message.tags
                )
                context.emit_funcs = [self.build_emit_func(chat_id=chat_id)]

                # Add an LLM to the context, using the Agent's if it exists.
                llm = None
                if hasattr(self.agent, "llm"):
                    llm = self.agent.llm
                else:
                    llm = OpenAI(client=self.client)

                context = with_llm(context=context, llm=llm)

                response = self.agent_service.run_agent(self.agent, context)
                if response is not None:
                    self.send(response)
                else:
                    # Do nothing here; this could be a message we intentionally don't want to respond to (ex. an image or file upload)
                    pass
            else:
                # Do nothing here; this could be a message we intentionally don't want to respond to (ex. an image or file upload)
                pass
        except Exception as e:
            response = self.response_for_exception(e, chat_id=chat_id)

            if chat_id is not None:
                self.send([response])
        # Even if we do nothing, make sure we return ok
        return InvocableResponse(string="OK")
