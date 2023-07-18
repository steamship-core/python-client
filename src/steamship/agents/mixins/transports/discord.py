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

DISCORD_API_BASE = "https://slack.com/api/"
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


class DiscordTransportConfig(Config):
    """Configuration object for the DiscordTransport."""

    slack_api_base: str = Field(
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

    def _manifest(self) -> dict:
        """Return the Slack Manifest which describes this app."""
        # When running in development, the below values will be none.
        invocable_instance_handle = (
            self.agent_service.context.invocable_instance_handle or "Development Steamship Agent"
        )
        invocable_handle = (
            self.agent_service.context.invocable_handle or "Development Steamship Agent"
        )

        # Slack only supports names of 25 characters or less
        invocable_instance_handle = invocable_instance_handle[:34]

        """Return the Slack Manifest for this Transport."""
        return {
            "display_information": {
                "name": invocable_instance_handle,
                "description": f"An instance of {self.agent_service.context.invocable_handle} powered by Steamship",
            },
            "features": {"bot_user": {"display_name": invocable_handle, "always_online": True}},
            "oauth_config": {
                "scopes": {
                    "bot": [
                        "commands",
                        "app_mentions:read",
                        "chat:write",
                        "chat:write.public",
                        "im:history",
                    ]
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
                "event_subscriptions": {
                    "bot_events": [
                        "app_home_opened",
                        "app_mention",
                        "message.app_home",
                        "message.im",
                    ],
                    "request_url": f"{self.agent_service.context.invocable_url}slack_event",
                },
            },
        }

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
        slack_blocks = None
        chat_id = None

        for block in blocks:
            # This is required for the public_url creation below.
            block.client = self.client

            if slack_blocks is None:
                slack_blocks = []

            if block.chat_id:
                chat_id = block.chat_id

            if block.is_text() or block.text:
                if not text:
                    # This is the fallback for mobile notifications
                    text = block.text
                # The real thing we send is a block
                if blocks is None:
                    blocks = []
                slack_blocks.append(
                    {"type": "section", "text": {"type": "mrkdwn", "text": block.text}}
                )
            elif block.is_image():
                image_url = block.to_public_url()
                slack_blocks.append(
                    {"type": "image", "image_url": image_url, "alt_text": image_url}
                )
            elif block.is_audio():
                audio_url = block.to_public_url()
                slack_blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"<{audio_url}|Audio Message>",
                        },
                    }
                )
            elif block.is_video():
                video_url = block.to_public_url()
                slack_blocks.append(
                    {"type": "video", "video_url": video_url, "alt_text": video_url}
                )
            else:
                logging.error(
                    f"Slack transport unable to send a block of MimeType {block.mime_type}"
                )

        bot_token = self.get_slack_access_token()
        if not bot_token:
            logging.error("Unable to send Slack Message: Slack transport had null bot token")
            return

        if not chat_id:
            logging.error("Unable to send Slack Message: no chat_id on output blocks")
            return

        headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json",
        }
        body = {
            "blocks": slack_blocks,
            "text": text,  # This is for mobile previews. The "block" key has the real content.
            "channel": chat_id,
        }

        post_url = f"{self.config.slack_api_base}chat.postMessage"

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
            slack_request = DiscordInteraction.parse_obj(kwargs)
            # TODO: For truly async requests, we'll have to find some way to plumb through the token.
            # For now it appears to be provided upon each inbound request.
            if slack_request.event:
                if slack_request.event.is_message():
                    logging.info(
                        f"User {slack_request.event.user} sent message in channel {slack_request.event.channel}"
                    )
                    incoming_messages = slack_request.event.to_blocks()
                    for incoming_message in incoming_messages:
                        if incoming_message is not None:
                            logging.info(f"Responding to {incoming_message}")
                            self._respond_to_block(incoming_message)
                elif slack_request.event.type == "app_home_opened":
                    logging.info(
                        f"User {slack_request.event.user} opened App Tab with channel {slack_request.event.channel}"
                    )
                    result = Block(text="Hi there!")
                    result.set_chat_id(slack_request.event.channel)
                    self.send([result])

        except BaseException as e:
            logging.error(e)
            chat_id = None
            if chat_id is not None:
                response = self.response_for_exception(e, chat_id=chat_id)
                if chat_id is not None:
                    self.send([response])

        # Even if we do nothing, make sure we return ok
        return InvocableResponse(string="OK")

    @post("slack_event", public=True)
    def slack_event(self, **kwargs) -> InvocableResponse[str]:
        """Respond to an inbound event from Slack."""
        return self._respond_to_webhook(**kwargs)

    @post("slack_respond", public=True)
    def slack_respond(self, **kwargs) -> InvocableResponse[str]:
        """Respond to an inbound event from Slack."""
        return self._respond_to_webhook(**kwargs)

    @post("set_slack_access_token")
    def set_slack_access_token(self, token: str) -> InvocableResponse[str]:
        """Set the slack access token."""
        kv = KeyValueStore(client=self.agent_service.client, store_identifier=SETTINGS_KVSTORE_KEY)
        kv.set("slack_token", {"token": token})
        return InvocableResponse(string="OK")

    def get_slack_access_token(self) -> Optional[str]:
        """Return the Slack Access token, which permits the agent to post to Slack."""
        if self.bot_token:
            return self.bot_token
        kv = KeyValueStore(client=self.agent_service.client, store_identifier=SETTINGS_KVSTORE_KEY)
        v = kv.get("slack_token")
        if not v:
            return None
        self.bot_token = v.get("token", None)
        return self.bot_token

    @post("is_slack_token_set")
    def is_slack_token_set(self) -> InvocableResponse[bool]:
        """Return whether the Slack token has been set as a way for a remote UI to check status."""
        token = self.get_slack_access_token()
        if token is None:
            return InvocableResponse(json=False)
        return InvocableResponse(json=True)
