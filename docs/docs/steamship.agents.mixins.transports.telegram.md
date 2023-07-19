<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/telegram.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.mixins.transports.telegram`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/telegram.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TelegramTransportConfig`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/telegram.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TelegramTransport`
Experimental base class to encapsulate a Telegram communication channel. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/telegram.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    client: Steamship,
    config: TelegramTransportConfig,
    agent_service: AgentService,
    agent: Agent
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/telegram.py#L171"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `build_emit_func`

```python
build_emit_func(
    chat_id: str
) → Callable[[List[Block], Dict[str, Any]], NoneType]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/mixins/transports/telegram.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `instance_init`

```python
instance_init(config: Config, invocation_context: InvocationContext)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `telegram_disconnect_webhook`

```python
telegram_disconnect_webhook(*args, **kwargs)
```

Unsubscribe from Telegram updates. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L179"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `telegram_respond`

```python
telegram_respond(**kwargs) → InvocableResponse[str]
```

Endpoint implementing the Telegram WebHook contract. This is a PUBLIC endpoint since Telegram cannot pass a Bearer token. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `telegram_webhook_info`

```python
telegram_webhook_info() → dict
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
