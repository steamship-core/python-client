<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/classification/zero_shot_classifier_tool.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.tools.classification.zero_shot_classifier_tool`




**Global Variables**
---------------
- **DEFAULT_LABELS**
- **DEFAULT_PROMPT**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/classification/zero_shot_classifier_tool.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ZeroShotClassifierTool`
Example tool to illustrate how one might classify a user message. 

For example: the agent may wish to know if the use message was a question, complaint, or suggestion. 

TODO: This feels like it wants to emit data to a side channel. Or perhaps it TAGS the user input block? 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/classification/zero_shot_classifier_tool.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    labels: Optional[List[str]] = None,
    rewrite_prompt: Optional[str] = None,
    **kwargs
)
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
