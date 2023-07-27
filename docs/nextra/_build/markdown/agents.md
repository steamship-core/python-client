<a id="building-agents"></a>

# Agents

Steamship is made for building, scaling, and managing Agents in the cloud.

A full tutorial for getting started with Agents is available here:

[Agent Guidebook](https://www.steamship.com/learn/agent-guidebook)

If you’re new to building Agents, we highly recommend following the above tutorial.

The following are pointers to the key Agent classes for getting started:

## Agent

The basic interface for Agents is:

[`steamship.agents.schema.agent.Agent`](/agents/../api/steamship.agents.schema.md#steamship.agents.schema.agent.Agent)

Implementations of this class make decisions about what Action will be taken next in an Agent workflow.

## AgentContext

The Agent Context contains data about the context in which the Agent is running, including its
ChatHistory.

## Tool

A Tool is something that an Agent may make use of in service of achieving its goal. To support multi-modal data,
Tools in Steamship take an AgentContext as input and produce [Blocks](/agents/../data/blocks.md#blocks) as output.

Many tools are available pre-packaged within the SDK:

- [`steamship.agents.tools.search.search.SearchTool`](/agents/../api/steamship.agents.tools.search.md#steamship.agents.tools.search.search.SearchTool)
- [`steamship.agents.tools.speech_generation.generate_speech.GenerateSpeechTool`](/agents/../api/steamship.agents.tools.speech_generation.md#steamship.agents.tools.speech_generation.generate_speech.GenerateSpeechTool) (via ElevenLabs)
- [`steamship.agents.tools.image_generation.dalle.DalleTool`](/agents/../api/steamship.agents.tools.image_generation.md#steamship.agents.tools.image_generation.dalle.DalleTool)
- [`steamship.agents.tools.image_generation.stable_diffusion.StableDiffusionTool`](/agents/../api/steamship.agents.tools.image_generation.md#steamship.agents.tools.image_generation.stable_diffusion.StableDiffusionTool)
- … and more in the `steamship.agents.tools` package.

## AgentService

[`steamship.agents.service.agent_service.AgentService`](/agents/../api/steamship.agents.service.md#steamship.agents.service.agent_service.AgentService)

The AgentService class provides a convenient way to deploy an Agent as a Steamship [Package](/agents/../packages/index.md#packages).

All  [`steamship.agents.service.agent_service.AgentService`](/agents/../api/steamship.agents.service.md#steamship.agents.service.agent_service.AgentService) instances contain a `prompt(self, prompt: str, **kwargs) -> List[Block]` method from thier base class.
This method is the core `chat` loop: it accepts an inbound `str` in the form of a user message, and it produces a list of multimodal `Block` objects that contain the response.
