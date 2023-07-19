<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/context.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.schema.context`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/context.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AgentContext`
AgentContext contains all relevant information about a particular execution of an Agent. It is used by the AgentService to manage execution history as well as store/retrieve information and metadata that will be used in the process of an agent execution. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/context.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__()
```






---

#### <kbd>property</kbd> id







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/context.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_or_create`

```python
get_or_create(
    client: Steamship,
    context_keys: Dict[str, str],
    tags: List[Tag] = None,
    searchable: bool = True
)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
