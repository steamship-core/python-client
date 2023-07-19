<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/binary_utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.utils.binary_utils`





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/binary_utils.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `guess_mime`

```python
guess_mime(obj: Any, provided_mime: str = None) → str
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/binary_utils.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `to_b64`

```python
to_b64(obj: Any) → str
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/binary_utils.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `flexi_create`

```python
flexi_create(
    base64string: str = None,
    data: Any = None,
    string: str = None,
    json: Any = None,
    _bytes: Union[bytes, BytesIO] = None,
    mime_type=None,
    force_base64=False
) → Tuple[Any, Optional[str], Optional[str]]
```

It's convenient for some constructors to accept a variety of input types: 
- data (your choice) 
- string 
- json 
- bytes 

.. And have them all homogenized. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
