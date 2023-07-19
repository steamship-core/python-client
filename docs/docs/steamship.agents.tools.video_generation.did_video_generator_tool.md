<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/video_generation/did_video_generator_tool.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.tools.video_generation.did_video_generator_tool`
Tool for generating images. 

**Global Variables**
---------------
- **DEFAULT_SOURCE_URL**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/video_generation/did_video_generator_tool.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DIDVideoGeneratorTool`
Tool to generate talking avatars from text using D-ID. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/video_generation/did_video_generator_tool.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```

Run the tool. Copied from base class to enable generate-time config overrides. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
