<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/local_server/server.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.cli.local_server.server`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/local_server/server.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ThreadedTCPServer`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/local_server/server.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SteamshipHTTPServer`
A simple HTTP Server that wraps an invocable (package or plugin). 

To use, call: 

 server = SteamshipHTTPServer(invocable)  server.start() 

To shut down, call: 

 server.stop() 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/local_server/server.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    invocable: Type[Invocable],
    base_url: Optional[str] = None,
    port: int = 8080,
    invocable_handle: str = None,
    invocable_version_handle: str = None,
    invocable_instance_handle: str = None,
    config: dict = None,
    workspace: str = None
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/local_server/server.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `start`

```python
start()
```

Start the server. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/local_server/server.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `stop`

```python
stop()
```

Stop the server. 

Note: This has to be called from a different thread or else it will deadlock. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
