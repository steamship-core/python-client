<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/client.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.base.client`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/client.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Client`
Client model.py class. 

Separated primarily as a hack to prevent circular imports. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/client.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    api_key: 'str' = None,
    api_base: 'str' = None,
    app_base: 'str' = None,
    web_base: 'str' = None,
    workspace: 'str' = None,
    fail_if_workspace_exists: 'bool' = False,
    profile: 'str' = None,
    config_file: 'str' = None,
    config: 'Configuration' = None,
    trust_workspace_config: 'bool' = False,
    **kwargs
)
```

Create a new client. 

If `workspace` is provided, it will anchor the client in a workspace by that name, creating it if necessary. Otherwise the `default` workspace will be used. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/client.py#L403"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `call`

```python
call(
    verb: 'Verb',
    operation: 'str',
    payload: 'Union[Request, dict]' = None,
    file: 'Any' = None,
    expect: 'Type[T]' = None,
    debug: 'bool' = False,
    raw_response: 'bool' = False,
    is_package_call: 'bool' = False,
    package_owner: 'str' = None,
    package_id: 'str' = None,
    package_instance_id: 'str' = None,
    as_background_task: 'bool' = False,
    wait_on_tasks: 'List[Union[str, Task]]' = None,
    timeout_s: 'Optional[float]' = None,
    task_delay_ms: 'Optional[int]' = None
) → Union[Any, Task]
```

Post to the Steamship API. 

All responses have the format:
``` 

```
.. code-block:: json 

 {  "data": "<actual response>",  "error": {"reason": "<message>"}  } # noqa: RST203 

For the Python client we return the contents of the `data` field if present, and we raise an exception if the `error` field is filled in. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/client.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `dict`

```python
dict(**kwargs) → dict
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/client.py#L589"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get`

```python
get(
    operation: 'str',
    payload: 'Union[Request, dict]' = None,
    file: 'Any' = None,
    expect: 'Any' = None,
    debug: 'bool' = False,
    raw_response: 'bool' = False,
    is_package_call: 'bool' = False,
    package_owner: 'str' = None,
    package_id: 'str' = None,
    package_instance_id: 'str' = None,
    as_background_task: 'bool' = False,
    wait_on_tasks: 'List[Union[str, Task]]' = None,
    timeout_s: 'Optional[float]' = None,
    task_delay_ms: 'Optional[int]' = None
) → Union[Any, Task]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/client.py#L626"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `logs`

```python
logs(
    offset: 'int' = 0,
    number: 'int' = 50,
    invocable_handle: 'Optional[str]' = None,
    instance_handle: 'Optional[str]' = None,
    invocable_version_handle: 'Optional[str]' = None,
    path: 'Optional[str]' = None,
    field_values: 'Optional[Dict[str, str]]' = None
) → Dict[str, Any]
```

Return generated logs for a client. 

The logs will be workspace-scoped. You will only receive logs for packages and plugins that you own. 

:param offset: The index of the first log entry to return. This can be used with `number` to page through logs. :param number: The number of log entries to return. This can be used with `offset` to page through logs. :param invocable_handle: Enables optional filtering based on the handle of package or plugin. Example: `my-package` :param instance_handle: Enables optional filtering based on the handle of package instance or plugin instance. Example: `my-instance` :param invocable_version_handle: Enables optional filtering based on the version handle of package or plugin. Example: `0.0.2` :param path: Enables optional filtering based on request path. Example: `/generate`. :param field_values: Enables optional filtering based on user-provided field values. :return: Returns a dictionary containing the offset and number of log entries as well as a list of `entries` that match the specificed filters. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/client.py#L552"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post`

```python
post(
    operation: 'str',
    payload: 'Union[Request, dict, BaseModel]' = None,
    file: 'Any' = None,
    expect: 'Any' = None,
    debug: 'bool' = False,
    raw_response: 'bool' = False,
    is_package_call: 'bool' = False,
    package_owner: 'str' = None,
    package_id: 'str' = None,
    package_instance_id: 'str' = None,
    as_background_task: 'bool' = False,
    wait_on_tasks: 'List[Union[str, Task]]' = None,
    timeout_s: 'Optional[float]' = None,
    task_delay_ms: 'Optional[int]' = None
) → Union[Any, Task]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/client.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `switch_workspace`

```python
switch_workspace(
    workspace_handle: 'str' = None,
    workspace_id: 'str' = None,
    fail_if_workspace_exists: 'bool' = False,
    trust_workspace_config: 'bool' = False
)
```

Switches this client to the requested workspace, possibly creating it. If all arguments are None, the client actively switches into the default workspace. 


- API calls are performed manually to not result in circular imports. 
- Note that the default workspace is technically not necessary for API usage; it will be assumed by the Engine  in the absense of a Workspace ID or Handle being manually specified in request headers. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
