<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/client/steamship.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.client.steamship`




**Global Variables**
---------------
- **SKILL_TO_PROVIDER**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/client/steamship.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Steamship`
Steamship Python Client. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/client/steamship.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/client/steamship.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `embed_and_search`

```python
embed_and_search(
    query: 'str',
    docs: 'List[str]',
    plugin_instance: 'str',
    k: 'int' = 1
) → QueryResults
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/client/steamship.py#L323"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_workspace`

```python
get_workspace() → Workspace
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/docs/steamship/client/steamship/temporary_workspace#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `temporary_workspace`

```python
temporary_workspace(**kwargs) → Generator['Steamship', None, None]
```

Create a client rooted in a temporary workspace that will be deleted after use. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/client/steamship.py#L125"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `use`

```python
use(
    package_handle: 'str',
    instance_handle: 'Optional[str]' = None,
    config: 'Optional[Dict[str, Any]]' = None,
    version: 'Optional[str]' = None,
    fetch_if_exists: 'bool' = True,
    workspace_handle: 'Optional[str]' = None,
    wait_for_init: 'bool' = True,
    **kwargs
) → PackageInstance
```

Creates/loads an instance of package `package_handle`. 

The instance is named `instance_handle` and located in the Workspace named `instance_handle`. If no `instance_handle` is provided, the default is `package_handle`. 

For example, one may write the following to always get back the same package instance, no matter how many times you run it, scoped into its own workspace: 

```python
instance = Steamship.use('package-handle', 'instance-handle')
``` 

One may also write: 

```python
instance = Steamship.use('package-handle') # Instance will also be named `package-handle`
``` 

If you wish to override the usage of a workspace named `instance_handle`, you can provide the `workspace_handle` parameter. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/client/steamship.py#L205"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `use_plugin`

```python
use_plugin(
    plugin_handle: 'str',
    instance_handle: 'Optional[str]' = None,
    config: 'Optional[Dict[str, Any]]' = None,
    version: 'Optional[str]' = None,
    fetch_if_exists: 'bool' = True,
    workspace_handle: 'Optional[str]' = None,
    wait_for_init: 'bool' = True,
    **kwargs
) → PluginInstance
```

Creates/loads an instance of plugin `plugin_handle`. 

The instance is named `instance_handle` and located in the Workspace named `instance_handle`. If no `instance_handle` is provided, the default is `plugin_handle`. 

For example, one may write the following to always get back the same plugin instance, no matter how many times you run it, scoped into its own workspace: 

```python
instance = Steamship.use_plugin('plugin-handle', 'instance-handle')
``` 

One may also write: 

```python
instance = Steamship.use('plugin-handle') # Instance will also be named `plugin-handle`
``` 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/client/steamship.py#L247"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `use_skill`

```python
use_skill(
    skill: 'Skill',
    provider: 'Optional[Vendor]' = None,
    instance_handle: 'Optional[str]' = None,
    fetch_if_exists: 'Optional[bool]' = True
) → PluginInstance
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
