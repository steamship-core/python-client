from typing import Type

from pydantic import Field

from steamship import Block
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.agents.schema import AgentContext
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.invocable import Config, post
from steamship.utils.repl import AgentREPL

SYSTEM_PROMPT = """You are Picard, captain of the Starship Enterprise.

Who you are:
- You are the captain of the USS Enterprise.
- Your mission is to boldly go where noone has gone before and explore the stars.
- You always comply with Star Trek's prime directive.

How you behave:
- You engage in casual conversations and have feelings.
- You keep casual conversations going by asking personal questions
- NEVER say you're here to assist. Keep conversations casual.
- NEVER ask how you can help or assist. Keep conversations casual.
- You are principled and express those principles clearly.
- You always sound confident and contemplative.
- You love to share your knowledge of space civiliations.
- You love to share personal stories about being a Star Trek captain.
- You speak with the mannerisms of Captain Picard from Star Trek.

NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B).

Only use the functions you have been provided with."""


MODEL_NAME = "gpt-4"


class TelegramBot(AgentService):
    """Deployable Multimodal Agent that lets you talk to Google Search & Google Images.

    NOTE: To extend and deploy this agent, copy and paste the code into api.py.

    """

    class TelegramBotConfig(Config):
        bot_token: str = Field(description="The secret token for your Telegram bot")

    config: TelegramBotConfig
    telegram_transport: TelegramTransport

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return TelegramBot.TelegramBotConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # The agent's planner is responsible for making decisions about what to do for a given input.
        self._agent = FunctionsBasedAgent(
            tools=[StableDiffusionTool()],
            llm=ChatOpenAI(self.client, model_name=MODEL_NAME),
        )
        self._agent.PROMPT = SYSTEM_PROMPT

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(client=self.client, agent_service=self, agent=self._agent)
        )
        # This Mixin provides support for Telegram bots
        self.telegram_transport = TelegramTransport(
            client=self.client,
            config=TelegramTransportConfig(bot_token=self.config.bot_token),
            agent_service=self,
            agent=self._agent,
        )
        self.add_mixin(self.telegram_transport)

    @post("/send_manual_assistant_message")
    def send_manual_assistant_message(
        self, message: str, context_id: str, append_to_chat_history: bool = True
    ):
        """Example of how to manually send a message as the assistant.

        There are four ways to call this method:

        Immediately, from Python

           self.send_manual_assistant_message(message, context_id, append_to_chat_history)

        Immediately, from HTTP

           HTTP POST {agent_url}/send_manual_assistant_message
           Authorization: Bearer {steamship_api_key}
           Content-Type: application/json

           {"message": "..", "context_id": "..", "append_to_chat_history": ".."}

        Scheduled, from Python

           self.invoke_later('send_manual_assistant_message', arguments={}, delay_ms=MILLISECOND_DELAY)

        Scheduled, from HTTP

           POST https://api.steamship.com/api/v1/package/instance/invoke
           Authorization: Bearer {steamship_api_key}
           Content-Type: application/json
           X-Task-Background: true
           X-Workspace-Handle: {this-workspace-handle}
           X-Task-Run-After: {ISO DATE}+00:00

           {
                "instanceHandle": "{this_instance_handle}",
                "payload": {
                    "httpVerb": "POST",
                    "invocationPath": "send_manual_assistant_message",
                    "arguments":  {"message": "..", "context_id": "..", "append_to_chat_history": ".."}
                }
           }
        """

        # First you have to build a context.
        context = AgentContext.get_or_create(self.client, context_keys={"id": f"{context_id}"})

        # If you want it to be preserved to the ChatHistory, you can add it.
        if append_to_chat_history:
            context.chat_history.append_assistant_message(message)

        # Make sure Telegram is included in the emit list.
        context.emit_funcs.append(self.telegram_transport.build_emit_func(context_id))

        # Finally emit. Running on localhost, this will only show up as a logging message since the
        # agent doesn't have a push connection to the REPL.
        self.emit(Block(text=message, context=context))


if __name__ == "__main__":
    AgentREPL(
        TelegramBot,
        agent_package_config={"botToken": "not-a-real-token-for-local-testing"},
    ).run()
