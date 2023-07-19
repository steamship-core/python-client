<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/llms/openai.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.llms.openai`




**Global Variables**
---------------
- **PLUGIN_HANDLE**
- **DEFAULT_MAX_TOKENS**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/llms/openai.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OpenAI`
LLM that uses Steamship's OpenAI plugin to generate completions. 

NOTE: By default, this LLM uses the `gpt-3.5-turbo` model. Valid model choices are `gpt-3.5-turbo` and `gpt-4`. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/llms/openai.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    client,
    model_name: str = 'gpt-3.5-turbo',
    temperature: float = 0.4,
    *args,
    **kwargs
)
```

Create a new instance. 

Valid model names are: 
 - gpt-4 
 - gpt-3.5-turbo 

Supported kwargs include: 
- `max_tokens` (controls the size of LLM responses) 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/llms/openai.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `complete`

```python
complete(prompt: str, stop: Optional[str] = None, **kwargs) → List[Block]
```

Completes the prompt, respecting the supplied stop sequence. 

Supported kwargs include: 
- `max_tokens` (controls the size of LLM responses) 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/llms/openai.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ChatOpenAI`
ChatLLM that uses Steamship's OpenAI plugin to generate chat completions. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/llms/openai.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client, model_name: str = 'gpt-4-0613', *args, **kwargs)
```

Create a new instance. 

Valid model names are: 
 - gpt-4 
 - gpt-4-0613 

Supported kwargs include: 
- `max_tokens` (controls the size of LLM responses) 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/llms/openai.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `chat`

```python
chat(messages: List[Block], tools: Optional[List[Tool]], **kwargs) → List[Block]
```

Sends chat messages to the LLM with functions from the supplied tools in a side-channel. 

Supported kwargs include: 
- `max_tokens` (controls the size of LLM responses) 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/llms/openai.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `complete`

```python
complete(prompt: str, stop: Optional[str] = None, **kwargs) → List[Block]
```

Completes the prompt, respecting the supplied stop sequence. 

Supported kwargs include: 
- `max_tokens` (controls the size of LLM responses) 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
