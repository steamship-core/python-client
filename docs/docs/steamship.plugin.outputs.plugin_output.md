<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/plugin_output.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.plugin.outputs.plugin_output`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/plugin_output.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OperationType`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/plugin_output.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OperationUnit`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/plugin_output.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UsageReport`
This is the report object that a plugin or package can send back to notify the engine how much of something was consumed 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/plugin_output.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_characters`

```python
run_characters(
    characters: int,
    audit_url: Optional[str] = None,
    audit_id: Optional[str] = None
)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/plugin_output.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_tokens`

```python
run_tokens(
    tokens: int,
    audit_url: Optional[str] = None,
    audit_id: Optional[str] = None
)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/plugin_output.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_units`

```python
run_units(
    units: int,
    audit_url: Optional[str] = None,
    audit_id: Optional[str] = None
)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/plugin_output.py#L77"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PluginOutput`
Base class for all types of plugin output, allowing usage reporting 







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
