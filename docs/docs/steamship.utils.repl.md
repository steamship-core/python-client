<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.utils.repl`





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `colored`

```python
colored(text: str, **kwargs)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SteamshipREPL`
Base class for building REPLs that facilitate running Steamship code in the IDE. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(log_level=None, dev_logging_handler=None)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_object`

```python
print_object(
    obj: Union[Task, Block, str, dict],
    metadata: Optional[Dict[str, Any]] = None
)
```

Print an object, returned by the agent or tool, to the console. 

Various epochs of the Agent SDK development have included Agents returning, to the repl: Blocks, strings, and Tasks. Since this is something that users can write (e.g. not controlled by the SDK) the REPL needs to handle all three cases in displaying output. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_object_or_objects`

```python
print_object_or_objects(
    output: Union[List, Any],
    metadata: Optional[Dict[str, Any]] = None
)
```

Print Agent or Tool output, whether a list or a single object. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_string`

```python
print_string(output: str, metadata: Optional[Dict[str, Any]] = None)
```

Print a string to console. All REPL output should ideally route through this method. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/docs/steamship/utils/repl/temporary_workspace#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `temporary_workspace`

```python
temporary_workspace() → Steamship
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ToolREPL`




<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(tool: Tool, client: Optional[Steamship] = None, **kwargs)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_object`

```python
print_object(
    obj: Union[Task, Block, str, dict],
    metadata: Optional[Dict[str, Any]] = None
)
```

Print an object, returned by the agent or tool, to the console. 

Various epochs of the Agent SDK development have included Agents returning, to the repl: Blocks, strings, and Tasks. Since this is something that users can write (e.g. not controlled by the SDK) the REPL needs to handle all three cases in displaying output. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_object_or_objects`

```python
print_object_or_objects(
    output: Union[List, Any],
    metadata: Optional[Dict[str, Any]] = None
)
```

Print Agent or Tool output, whether a list or a single object. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_string`

```python
print_string(output: str, metadata: Optional[Dict[str, Any]] = None)
```

Print a string to console. All REPL output should ideally route through this method. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L138"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_with_client`

```python
run_with_client(client: Workspace, context: Optional[AgentContext] = None)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/docs/steamship/utils/repl/temporary_workspace#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `temporary_workspace`

```python
temporary_workspace() → Steamship
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L143"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AgentREPL`




<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L150"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    agent_class: Type[AgentService],
    method: Optional[str] = None,
    agent_package_config: Optional[Dict[str, Any]] = None,
    client: Optional[Steamship] = None,
    context_id: Optional[str] = None,
    **kwargs
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_object`

```python
print_object(
    obj: Union[Task, Block, str, dict],
    metadata: Optional[Dict[str, Any]] = None
)
```

Print an object, returned by the agent or tool, to the console. 

Various epochs of the Agent SDK development have included Agents returning, to the repl: Blocks, strings, and Tasks. Since this is something that users can write (e.g. not controlled by the SDK) the REPL needs to handle all three cases in displaying output. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_object_or_objects`

```python
print_object_or_objects(
    output: Union[List, Any],
    metadata: Optional[Dict[str, Any]] = None
)
```

Print Agent or Tool output, whether a list or a single object. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_string`

```python
print_string(output: str, metadata: Optional[Dict[str, Any]] = None)
```

Print a string to console. All REPL output should ideally route through this method. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L188"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(**kwargs)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L167"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_with_client`

```python
run_with_client(client: Steamship, **kwargs)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/docs/steamship/utils/repl/temporary_workspace#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `temporary_workspace`

```python
temporary_workspace() → Steamship
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L193"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `HttpREPL`
REPL that uses an HTTP endpoint. Best for the `ship serve` command. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L201"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    prompt_url: str,
    context_id: Optional[str] = None,
    client: Optional[Steamship] = None,
    **kwargs
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_object`

```python
print_object(
    obj: Union[Task, Block, str, dict],
    metadata: Optional[Dict[str, Any]] = None
)
```

Print an object, returned by the agent or tool, to the console. 

Various epochs of the Agent SDK development have included Agents returning, to the repl: Blocks, strings, and Tasks. Since this is something that users can write (e.g. not controlled by the SDK) the REPL needs to handle all three cases in displaying output. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_object_or_objects`

```python
print_object_or_objects(
    output: Union[List, Any],
    metadata: Optional[Dict[str, Any]] = None
)
```

Print Agent or Tool output, whether a list or a single object. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print_string`

```python
print_string(output: str, metadata: Optional[Dict[str, Any]] = None)
```

Print a string to console. All REPL output should ideally route through this method. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L263"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(**kwargs)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/repl.py#L213"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_with_client`

```python
run_with_client(client: Steamship, **kwargs)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/docs/steamship/utils/repl/temporary_workspace#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `temporary_workspace`

```python
temporary_workspace() → Steamship
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
