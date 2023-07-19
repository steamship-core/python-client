<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/indexer_pipeline_mixin.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.mixins.indexer_pipeline_mixin`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/indexer_pipeline_mixin.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `IndexerPipelineMixin`
Provides a complete set of endpoints & async workflow for Document Question Answering. 

This Mixin is an async orchestrator of other mixins: 
- Importer Mixin:       to import files, e.g. YouTube videos, PDF urls 
- Blockifier Mixin:     to convert files to Blocks -- whether that's s2t or PDF parsing, etc. 
- Indexer Mixin:        to convert Steamship Files to embedded sharts 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/indexer_pipeline_mixin.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Steamship, invocable: PackageService)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `index_url`

```python
index_url(
    url: str,
    metadata: Optional[dict] = None,
    index_handle: Optional[str] = None,
    mime_type: Optional[str] = None
) → Task
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_file_status`

```python
set_file_status(file_id: str, status: str) → bool
```

Set the status bit of a file. Intended to be scheduled after import. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
