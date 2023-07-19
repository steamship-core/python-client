<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/steamship_widget.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.mixins.transports.steamship_widget`




**Global Variables**
---------------
- **API_BASE**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/steamship_widget.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SteamshipWidgetTransport`
Experimental base class to encapsulate a Steamship web widget communication channel. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/steamship_widget.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Steamship, agent_service: AgentService, agent: Agent)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `answer`

```python
answer(**payload) → List[Block]
```

Endpoint that implements the contract for Steamship embeddable chat widgets. This is a PUBLIC endpoint since these webhooks do not pass a token. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `info`

```python
info() → dict
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/steamship_widget.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `instance_init`

```python
instance_init(config: Config, context: InvocationContext)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/steamship_widget.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save_for_emit`

```python
save_for_emit(blocks: List[Block], metadata: Dict[str, Any])
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
