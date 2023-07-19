<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/config.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.config`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/config.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Config`
Base class Steamship Package and Plugin configuration objects. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/config.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(**kwargs)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/config.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `extend_with_dict`

```python
extend_with_dict(d: dict, overwrite: bool = False)
```

Sets the attributes on this object with provided keys and values. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/config.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `extend_with_json_file`

```python
extend_with_json_file(
    path: Path,
    overwrite: bool = False,
    fail_on_missing_file: bool = True
)
```

Extends this config object's values with a JSON file from disk. 

This is useful for applying late-bound defaults, such as API keys added to a deployment bundle. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/config.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_config_parameters`

```python
get_config_parameters() → Dict[str, ConfigParameter]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/config.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `strip_enum`

```python
strip_enum(default_value)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
