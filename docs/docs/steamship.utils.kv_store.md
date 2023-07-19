<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/kv_store.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.utils.kv_store`
A simple key-value store implemented atop Files and Tags. 

**Global Variables**
---------------
- **KV_STORE_MARKER**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/kv_store.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `KeyValueStore`
A simple key value store implemented in Steamship. 

Instances of the KeyValueStore are identified by its  `namespace`. This store_identifier corresponds to a File that will be created with a special tag identifying it. 

Entries of the KeyValueStore are saved as `Tag` objects with:  * Kind = "KeyValueStore"  * Name = the key of the (kv) pair  * Value = a dict set to the value 

Note that the value is always saved as a dict object. To save a string or int, wrap it in a dict. 

WARNING: 

This is essentially a clever hack atop Steamship's tag system to provide mutable key-value storage. It is in the steamship.utils package because it's proven useful once or twice. But in general, if you find yourself heavily relying upon it, consider reaching out to us at hello@steamship.com to let us know, and we'll up-prioritize adding a proper key-value API. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/kv_store.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Steamship, store_identifier: str = 'KeyValueStore')
```

Create a new KeyValueStore instance. 



**Args:**
 
 - <b>`client`</b> (Steamship):  The Steamship client. 
 - <b>`store_identifier`</b> (str):  The store_identifier which identifies this KeyValueStore instance. You can have multiple, separate KeyValueStore instances in a workspace using this implementation. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/kv_store.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete`

```python
delete(key: str) → bool
```

Delete the entry represented by `key` 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/kv_store.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get`

```python
get(key: str) → Optional[Dict]
```

Get the value represented by `key`. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/kv_store.py#L95"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `items`

```python
items(
    filter_keys: Optional[List[str]] = None
) → List[Tuple[str, Dict[str, Any]]]
```

Return all key-value entries as a list of (key, value) tuples. 

If `filter_keys` is provided, only returns keys within that list. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/kv_store.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `reset`

```python
reset()
```

Delete all key-values. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/kv_store.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set`

```python
set(key: str, value: Dict[str, Any])
```

Set the entry (key, value). 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
