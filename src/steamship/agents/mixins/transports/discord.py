import json
import logging
import urllib.parse
from typing import List, Optional

import requests
from pydantic import BaseModel, Field

from steamship import Block, Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.mixins.transports.transport import Transport
from steamship.agents.schema import Agent, AgentContext, EmitFunc, Metadata
from steamship.agents.service.agent_service import AgentService
from steamship.agents.utils import with_llm
from steamship.invocable import Config, InvocableResponse, InvocationContext, get, post
from steamship.utils.kv_store import KeyValueStore

DISCORD_API_BASE = "https://discord.com/api/v9/"
SETTINGS_KVSTORE_KEY = "discord-transport"


class DiscordUser(BaseModel):
    id: Optional[str] = Field(description="ID of the channel")
    username: Optional[str] = Field(description="Username of the channel")
    discriminator: Optional[str] = Field(description="the user's Discord-tag")
    global_name: Optional[str] = Field(
        description="the user's display name, if it is set. For bots, this is the application name"
    )
    email: Optional[str] = Field(description="the user's email")
    bot: Optional[bool] = Field(description="whether the user belongs to an OAuth2 application")


class DiscordMessage(BaseModel):
    id: Optional[str] = Field(description="ID of the message")
    channel_id: Optional[str] = Field(description="ID of the channel")
    author: Optional[DiscordUser] = Field(description="User who wrote it")
    content: Optional[str] = Field(description="Content of the message")
    timestamp: Optional[str] = Field(description="ISO8601 timestamp")
    type: Optional[int] = Field(
        description="Type of message"  # DEFAULT 0; REPLY 19; THREAD_STARTER_MESSAGE 21,
    )

    def to_blocks(self) -> List[Block]:
        ret = []
        if self.content:
            block = Block(text=self.content)
            block.set_chat_id(str(self.channel_id))
            # TODO: Set other metadata on block
            ret.append(block)
        return ret


class DiscordChannel(BaseModel):
    id: Optional[str] = Field(description="ID of the channel")
    name: Optional[str] = Field(description="Name of the channel")


class DiscordInteraction(BaseModel):
    """The message a Discord application receives when a user uses an application command or a message component.

    https://discord.com/developers/docs/interactions/receiving-and-responding
    """

    id: Optional[str] = Field(description="ID of the interaction")
    application_id: Optional[str] = Field(
        description="ID of the application this interaction is for."
    )
    type: Optional[str] = Field(
        description="Interaction type."  # PING = 1, APP COMMAND = 2, MESSAGE COMPONENT = 3, APP CMD AUTOCOMPLETE = 4, MODAL SUBMIT = 5
    )
    message: Optional[DiscordMessage] = Field(
        description="For components, the message they were attached to"
    )
    user: Optional[DiscordUser] = Field(
        description="User object for the invoking user, if invoked in a DM"
    )
    token: Optional[str] = Field(description=" token for responding to the interaction")
    channel_id: Optional[str] = Field(description="Channel that the interaction was sent from")
    channel: Optional[DiscordChannel] = Field(
        description="Channel that the interaction was sent from"
    )

    def is_message(self) -> bool:
        return self.type == 3

    def to_blocks(self) -> List[Block]:
        ret = []
        if self.message:
            for block in self.message.to_blocks():
                ret.append(block)
        return ret


class DiscordTransportConfig(Config):
    """Configuration object for the DiscordTransport."""

    discord_api_base: str = Field(
        DISCORD_API_BASE, description="Slack API base URL. If blank defaults to production Slack."
    )


class DiscordTransport(Transport):
    """Discord Transport Mixin for Steamship Agent to Discord interaction."""

    bot_token: str
    agent: Agent
    agent_service: AgentService
    config: DiscordTransportConfig

    def __init__(
        self,
        client: Steamship,
        config: DiscordTransportConfig,
        agent_service: AgentService,
        agent: Agent,
    ):
        super().__init__(client=client)
        self.bot_token = None
        self.agent = agent
        self.agent_service = agent_service
        self.config = config

    def instance_init(self, config: Config, invocation_context: InvocationContext):
        """Called when the owning AgentService initializes for the first time."""
        pass

    def _manifest_url(self) -> str:
        """Return the Manifest Installation URL of the Bot."""
        manifest_dict = self._manifest()
        manifest_json = json.dumps(manifest_dict)
        manifest_str = urllib.parse.quote(manifest_json)
        return f"https://api.slack.com/apps?new_app=1&manifest_json={manifest_str}"

    @get("slack_install_link", public=True)
    def slack_install_link(self) -> str:
        """Return the link to install this Agent as a Slack bot."""
        return self._manifest_url()

    def _send(self, blocks: List[Block], metadata: Metadata):  # noqa: C901
        """Send a response to the Slack chat.

        Slack uses the `text` field for fallback.
        But we want to also provide the blocks and attachments for multiple messages that are multi-modal
        """

        text = None
        embeds = None
        chat_id = None

        for block in blocks:
            # This is required for the public_url creation below.
            block.client = self.client

            if embeds is None:
                embeds = []

            if block.chat_id:
                chat_id = block.chat_id

            if block.is_text() or block.text:
                if not text:
                    # This is the fallback for mobile notifications
                    text = block.text
                else:
                    text = f"{text}\n{block.text}"
            elif block.is_image():
                url = block.to_public_url()
                embeds.append({"type": "image", "url": url})
            elif block.is_audio():
                url = block.to_public_url()
                embeds.append({"type": "link", "url": url})
            elif block.is_video():
                url = block.to_public_url()
                embeds.append({"type": "video", "url": url})
            else:
                logging.error(
                    f"Discord transport unable to send a block of MimeType {block.mime_type}"
                )

        bot_token = self.get_discord_access_token()
        if not bot_token:
            logging.error("Unable to send Discord Message: Discord transport had null bot token")
            return

        if not chat_id:
            logging.error("Unable to send Discord Message: no chat_id on output blocks")
            return

        headers = {
            "Authorization": f"{bot_token}",
            "Content-Type": "application/json",
        }
        body = {
            "content": text,
            #            'nonce': str(random.randint(10 ** 18, 10 ** 18 + 2 * (10 ** 17))),
            "tts": False,
        }

        post_url = f"{self.config.discord_api_base}channels/{chat_id}/messages"

        requests.post(post_url, headers=headers, json=body)

    def build_emit_func(self, chat_id: str) -> EmitFunc:
        """Return an EmitFun that sends messages to the appropriate Slack channel."""

        def new_emit_func(blocks: List[Block], metadata: Metadata):
            for block in blocks:
                block.set_chat_id(chat_id)
            return self.send(blocks, metadata)

        return new_emit_func

    def _respond_to_block(self, incoming_message: Block):
        """Respond to a single inbound message from Slack, posting the response back to Slack."""
        try:
            chat_id = incoming_message.chat_id

            if not chat_id:
                logging.error(f"No chat id on incoming block {incoming_message}")
                return

            # TODO: It feels like context is something the Agent should be providing.
            context = AgentContext.get_or_create(self.client, context_keys={"chat_id": chat_id})
            context.chat_history.append_user_message(
                text=incoming_message.text, tags=incoming_message.tags
            )
            # TODO: For truly async support, this emit fn will need to be wired in at the Agent level.
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

        except BaseException as e:
            logging.error(e)
            if chat_id is not None:
                response = self.response_for_exception(e, chat_id=chat_id)
                if chat_id is not None:
                    self.send([response])

    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        """Note: This is required by the superclass, but the return value of the interface (Block) doesn't match
        what Slack will send (List[Block]). A longer term TODO is refactor the base class, but until the Slack class
        is of acceptable quality, it feels like that would be putting too much into one PR."""
        return None

    def _respond_to_webhook(self, **kwargs) -> InvocableResponse[str]:
        """Respond to inbound Slack events. This is a PUBLIC endpoint."""
        try:
            discord_request = DiscordInteraction.parse_obj(kwargs)
            if discord_request.is_message():
                logging.info(
                    f"User {discord_request.user} sent message in channel {discord_request.channel_id}"
                )
                incoming_messages = discord_request.to_blocks()
                for incoming_message in incoming_messages:
                    if incoming_message is not None:
                        logging.info(f"Responding to {incoming_message}")
                        self._respond_to_block(incoming_message)

        except BaseException as e:
            logging.error(e)
            chat_id = None
            if chat_id is not None:
                response = self.response_for_exception(e, chat_id=chat_id)
                if chat_id is not None:
                    self.send([response])

        # Even if we do nothing, make sure we return ok
        return InvocableResponse(string="OK")

    @post("discord_respond", public=True)
    def discord_respond(self, **kwargs) -> InvocableResponse[str]:
        """Respond to an inbound event from Slack."""
        return self._respond_to_webhook(**kwargs)

    @post("set_discord_access_token")
    def set_discord_access_token(self, token: str) -> InvocableResponse[str]:
        """Set the discord access token."""
        kv = KeyValueStore(client=self.agent_service.client, store_identifier=SETTINGS_KVSTORE_KEY)
        kv.set("discord_token", {"token": token})
        return InvocableResponse(string="OK")

    def get_discord_access_token(self) -> Optional[str]:
        """Return the Discord Access token, which permits the agent to post to Discord."""
        if self.bot_token:
            return self.bot_token
        kv = KeyValueStore(client=self.agent_service.client, store_identifier=SETTINGS_KVSTORE_KEY)
        v = kv.get("discord_token")
        if not v:
            return None
        self.bot_token = v.get("token", None)
        return self.bot_token

    @post("is_discord_token_set")
    def is_discord_token_set(self) -> InvocableResponse[bool]:
        """Return whether the Discord token has been set as a way for a remote UI to check status."""
        token = self.get_discord_access_token()
        if token is None:
            return InvocableResponse(json=False)
        return InvocableResponse(json=True)
