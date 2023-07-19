<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/error.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.base.error`




**Global Variables**
---------------
- **DEFAULT_ERROR_MESSAGE**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/error.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SteamshipError`




<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/error.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    message: 'str' = 'Undefined remote error',
    internal_message: 'str' = None,
    suggestion: 'str' = None,
    code: 'str' = None,
    error: 'Union[Exception, str]' = None
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/error.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `from_dict`

```python
from_dict(d: 'Any') → SteamshipError
```

Last resort if subclass doesn't override: pass through. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/error.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `log`

```python
log()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/error.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_dict`

```python
to_dict() → dict
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
