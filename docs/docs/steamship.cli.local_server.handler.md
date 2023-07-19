<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/local_server/handler.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.cli.local_server.handler`





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/local_server/handler.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_safe_handler`

```python
create_safe_handler(invocable: Type[Invocable] = None)
```

Mimics the create_safe_handler function in lambda_handler for parallelism. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/local_server/handler.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `make_handler`

```python
make_handler(
    invocable_class: Type[Invocable],
    base_url: Optional[str] = 'http://localhost',
    default_api_key: Optional[str] = None,
    invocable_handle: str = None,
    invocable_version_handle: str = None,
    invocable_instance_handle: str = None,
    config: dict = None,
    workspace: str = None
)
```

Creates and returns a SimpleHTTPRequestHandler class for an Invocable (package or plugin). 

For use with steamship.cli.http.server.Server. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
