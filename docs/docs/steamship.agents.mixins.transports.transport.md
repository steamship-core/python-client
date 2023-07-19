<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/transport.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.mixins.transports.transport`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/transport.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Transport`




<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/transport.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/transport.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `parse_inbound`

```python
parse_inbound(payload: dict, context: Optional[dict] = None) → Optional[Block]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/transport.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `response_for_exception`

```python
response_for_exception(
    e: Optional[Exception],
    chat_id: Optional[str] = None
) → Block
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/transport.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `send`

```python
send(blocks: List[Block], metadata: Optional[Dict[str, Any]] = None)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
