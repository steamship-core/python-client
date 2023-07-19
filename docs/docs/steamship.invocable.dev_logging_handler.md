<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/dev_logging_handler.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.dev_logging_handler`




**Global Variables**
---------------
- **LOGGING_FORMAT**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/dev_logging_handler.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DevelopmentLoggingHandler`
A logging handler for developing Steamship Agents, Tools, Packages, and Plugins locally. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/dev_logging_handler.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    log_level: <built-in function any> = 30,
    log_level_for_messages: <built-in function any> = 20,
    file_log_level: <built-in function any> = 20
)
```






---

#### <kbd>property</kbd> name







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/dev_logging_handler.py#L82"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `emit`

```python
emit(record)
```

Emit the record, printing it to console out. 

We rely on TWO logging levels for the mechanics of this LoggingHandler: 


- One for standard logging 
- One for specific system Agent-related events, flagged with metadata 

This is to permit INFO-level logging of key Agent/Tool actions without committing the user to see all INFO-level logging globally. 

A future implementation may use a cascade of loggers attached to the AgentContext to do this more cleanly. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/dev_logging_handler.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `init_and_take_root`

```python
init_and_take_root(
    log_level: <built-in function any> = 20
) → DevelopmentLoggingHandler
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
