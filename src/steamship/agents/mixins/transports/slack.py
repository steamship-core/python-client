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

SLACK_API_BASE = "https://slack.com/api/"
SETTINGS_KVSTORE_KEY = "slack-transport"


class SlackElement(BaseModel):
    """An element of a Slack Block."""

    type: Optional[str] = Field(description="Type of block")
    """Common types are:
        - rich_text_section
        - user
        - text
    """
    elements: Optional[List["SlackElement"]] = Field(description="Element")
    user_id: Optional[str] = Field(description="The user id that created the element")
    text: Optional[str] = Field(description="The text of the element. Does not contain the user")

    def to_blocks(self) -> Optional[List[Block]]:
        """Return self as a list of Steamship Blocks."""
        ret = []

        if self.elements:
            for element in self.elements or []:
                for block in element.to_blocks() or []:
                    ret.append(block)
        elif self.text:
            block = Block(text=self.text)
            ret.append(block)
        return ret


class SlackBlock(BaseModel):
    """A Slack Block."""

    type: Optional[str] = Field(description="Type of block")
    """Common types are:
        - rich_text
    """
    block_id: Optional[str] = Field(description="ID of the block")
    elements: Optional[List[SlackElement]] = Field(description="Element")

    def to_blocks(self) -> Optional[List[Block]]:
        """Return self as a list of Steamship Blocks."""

        ret = []
        for element in self.elements or []:
            for block in element.to_blocks() or []:
                ret.append(block)
        return ret


class SlackEvent(BaseModel):
    """A Slack Event as reported to the Bot."""

    type: Optional[str] = Field(description="Type of event")
    """Common types are:
        - app_home_opened
        - app_mention,
        - reaction_added
        - message.channels - A message was posted to a channel
        - message.groups - A message was posted to a private channel
        - message.im - A message was posted to a DM
        - message.mpim - A message was posted to a Group DM
        - message.app_home - A message was posted to the "App Home" chat
        - hello - The client has connected to the server

    See more at: https://api.slack.com/events

    """
    user: Optional[str] = Field(
        description="The user ID belonging to the user that incited this action. Not included in all events as not all events are controlled by users. This is not the Slack handle."
    )
    channel: Optional[str] = Field(description="Channel of the event")
    tab: Optional[str] = Field(description="Tab in which the event occurred")
    event_ts: Optional[str] = Field(
        description="Timestamp of the event. A string, but is a floating point number within that."
    )
    ts: Optional[str] = Field(
        description="Timestamp of the message. A string, but is a floating point number within that."
    )
    item: Optional[str] = Field(
        description="Data specific to the underlying object type being described."
    )
    client_msg_id: Optional[str] = Field(description="")
    text: Optional[str] = Field(
        description="The text preview of the sequence of messages. Contains the user ID."
    )
    blocks: Optional[List[SlackBlock]] = Field(
        description="The text preview of the sequence of messages"
    )
    team: Optional[str] = Field(description="The team from which the message came")
    bot_id: Optional[str] = Field(
        description="The unique identifier for the bot that sent the event."
    )

    def is_message(self) -> bool:
        """Return whether this event is a message"""
        return self.type and (self.type.startswith("message") or self.type == "app_mention")

    def to_blocks(self) -> Optional[List[Block]]:
        """Return self as a list of Steamship Blocks."""

        ret = []
        for slack_block in self.blocks or []:
            for block in slack_block.to_blocks() or []:
                if self.channel:
                    block.set_chat_id(str(self.channel))
                # TODO: Do we want to encode other things like the tab, user, etc?
                ret.append(block)
        return ret


class SlackRequest(BaseModel):
    """The outer object presented when Slack sends a webhook notification.

    https://api.slack.com/apis/connections/events-api#event-type-structure
    """

    token: Optional[str] = Field(
        description="The shared-private callback token that authenticates this callback to the application as having come from Slack. Match this against what you were given when the subscription was created. If it does not match, do not process the event and discard it."
    )
    team_id: Optional[str] = Field(
        description="The unique identifier for the workspace/team where this event occurred."
    )

    api_app_id: Optional[str] = Field(
        description="The unique identifier for the application this event is intended for."
    )
    event: Optional[SlackEvent] = Field(description="Slack event")
    type: Optional[str] = Field(description="The type of inbound request")  # event_callback
    event_id: Optional[str] = Field(description="The event ID")
    event_time: Optional[int] = Field(description="The event time")
    event_context: Optional[str] = Field(description="The event context key")


class SlackTransportConfig(Config):
    """Configuration object for the SlackTransport."""

    # TODO: This is a placeholder for a V2 to include a choice of what kind of scope you wish your bot to have.
    #       For example: only reply to direct mentions? Listen to ALL messages?

    slack_api_base: str = Field(
        SLACK_API_BASE, description="Slack API base URL. If blank defaults to production Slack."
    )


class SlackTransport(Transport):
    # noqa: RST204
    """Slack Transport Mixin for Steamship Agent to Slack interaction.

    Current support:
    - Outputs: outputs: text, image, video, audio output
    - Inputs: text
    - Message-triggering events: direct mention, bot room entry

    The included manifest file below will register a Slack bot which can be added to rooms and communicated
    with directly. As configured below, it will not receive messages that were not intended for it.

    Integration flow:

    Slack needs a different style of integration than Telegram, involving a two-way handshake.

    The user:

    1) Clicks a "Bot Manifest Link" which is generated by your Steamship Agent Instance
       This manifest link contains requested access as well as callback URL information.
    2) Clicks "Accept" to create a Slack Bot using that manifest.
    3) Clicks "Install" to install the Slack Bot to a workspace, accepting the permissions
    4) Copy the Oauth Token from the "Settings > Install App" page.
    5) Set the Oauth token for your agent using the set_slack_access_token POST method

    At this point, (1) Slack knows about the Agent, and (2) the Agent knows about Slack.

    Interacting with the Bot on Slack will trigger a request/response loop in the Agent.
    """

    bot_token: str
    agent: Agent
    agent_service: AgentService
    config: SlackTransportConfig

    def __init__(
        self,
        client: Steamship,
        config: SlackTransportConfig,
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

        requests.post(
            post_url,
            headers=headers,
            json=body,
        )

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

    @post("respond_to_webhook")
    def respond_to_webhook(self, **kwargs) -> InvocableResponse[str]:  # noqa: C901
        """Respond to inbound Slack events. This is a PUBLIC endpoint."""
        try:
            slack_request = SlackRequest.parse_obj(kwargs)
            # TODO: For truly async requests, we'll have to find some way to plumb through the token.
            # For now it appears to be provided upon each inbound request.
            if slack_request.event:
                if slack_request.event.bot_id is None:
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
        self.agent_service.invoke_later("respond_to_webhook", arguments=kwargs)
        return InvocableResponse(string="OK")

    @post("slack_respond", public=True)
    def slack_respond(self, **kwargs) -> InvocableResponse[str]:
        """Respond to an inbound event from Slack."""
        self.agent_service.invoke_later("respond_to_webhook", arguments=kwargs)
        return InvocableResponse(string="OK")

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
