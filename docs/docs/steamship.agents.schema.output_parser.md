<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/output_parser.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.schema.output_parser`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/output_parser.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OutputParser`
Used to convert text into Actions. 

Primarily used by LLM-based agents that generate textual descriptions of selected actions and their inputs. OutputParsers can be used to convert those descriptions into Action objects for the AgentService to run. 



**Example:**
 
 - input: "Action: GenerateImage  ActionInput: row-house" 
 - output: Action("dalle", "row-house") 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/output_parser.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `parse`

```python
parse(text: str, context: AgentContext) → Action
```

Convert text into an Action object. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
