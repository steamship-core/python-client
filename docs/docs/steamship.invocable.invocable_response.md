<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable_response.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.invocable_response`




**Global Variables**
---------------
- **DEFAULT_ERROR_MESSAGE**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable_response.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Http`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable_response.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `InvocableResponse`
Mirrors the Response object in the Steamship server. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable_response.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    status: 'Task' = None,
    error: 'SteamshipError' = None,
    http: 'Http' = None,
    data: 'Any' = None,
    string: 'str' = None,
    json: 'Any' = None,
    _bytes: 'Union[bytes, BytesIO]' = None,
    mime_type=None
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable_response.py#L116"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `error`

```python
error(
    code: 'int',
    message: 'Optional[str]' = None,
    error: 'Optional[SteamshipError]' = None,
    exception: 'Optional[Exception]' = None,
    prefix: 'Optional[str]' = None
) → InvocableResponse[T]
```

Merges a number of error channels into one unified Response object. 

Aggregates all possible messages into a single " | "-delimeted error message. 

If the final resulting error message is non-null, prefixes with the provided `prefix` 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable_response.py#L157"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `from_obj`

```python
from_obj(obj: 'Any') → InvocableResponse
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable_response.py#L187"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_update`

```python
post_update(client: 'Client')
```

Pushes this response object to the corresponding Task on the Steamship Engine. 

Typically apps and plugins return their results to the Engine synchronously via HTTP. But sometimes that's not practice -- for example: 


- Microsoft's OCR endpoint returns a Job Token that can be exchanged for updates, and eventually a result. 
- Google's AutoML can take 20-30 minutes to train. 
- Fine-tuning BERT on ECS can take an arbitrarily long amount of time. 

In these cases, it can be useful for the package/plugin to occasionally post updates to the Engine outside of the Engine's initial synchronous request-response conversation. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable_response.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_data`

```python
set_data(
    data: 'Any' = None,
    string: 'str' = None,
    json: 'Any' = None,
    _bytes: 'Union[bytes, BytesIO]' = None,
    mime_type=None
)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
