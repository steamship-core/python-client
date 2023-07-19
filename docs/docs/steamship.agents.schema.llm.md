<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/llm.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.schema.llm`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/llm.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LLM`
LLM wraps large language model-based backends. 

They may be used with LLMAgents in Action selection, or for direct prompt completion. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/llm.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `complete`

```python
complete(prompt: str, stop: Optional[str] = None, **kwargs) → List[Block]
```

Completes the provided prompt, stopping when the stop sequeunce is found. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/llm.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ChatLLM`
ChatLLM wraps large language model-based backends that use a chat completion style interation. 

They may be used with Agents in Action selection, or for direct prompt completion. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/llm.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `chat`

```python
chat(messages: List[Block], tools: Optional[List[Tool]], **kwargs) → List[Block]
```

Sends the set of chat messages to the LLM, returning the next part of the conversation 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
