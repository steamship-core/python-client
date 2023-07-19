<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/indexer_mixin.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.mixins.indexer_mixin`




**Global Variables**
---------------
- **DEFAULT_EMBEDDING_INDEX_CONFIG**
- **DEFAULT_EMBEDDING_INDEX_HANDLE**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/indexer_mixin.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `IndexerMixin`
Provides endpoints for easy Indexing of blockified files. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/indexer_mixin.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    client: Steamship,
    embedder_config: dict = None,
    context_window_size: int = 200,
    context_window_overlap: int = 50
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `index_block`

```python
index_block(
    block_id: str,
    metadata: Optional[dict] = None,
    index_handle: Optional[str] = None
)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L121"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `index_file`

```python
index_file(
    file_id: str,
    metadata: Optional[dict] = None,
    index_handle: Optional[str] = None
) → bool
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L70"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `index_text`

```python
index_text(
    text: str,
    metadata: Optional[dict] = None,
    index_handle: Optional[str] = None
) → bool
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L134"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `search_index`

```python
search_index(
    query: str,
    index_handle: Optional[str] = None,
    k: int = 5
) → SearchResults
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
