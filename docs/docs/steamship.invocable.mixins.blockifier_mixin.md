<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/blockifier_mixin.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.mixins.blockifier_mixin`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/blockifier_mixin.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `BlockifierMixin`
Provides endpoints for easy Blockification of files. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/blockifier_mixin.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Steamship)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `blockify`

```python
blockify(
    file_id: str,
    mime_type: Optional[MimeTypes] = None,
    blockifier_handle: Optional[str] = None,
    after_task_id: Optional[str] = None
) → Task
```

Blockify the file `file_id` using a curated set of defaults for the provided `mime_type`. 

If no MIME Type is provided, the file's recorded MIME Type will be used. If still no MIME Type is available, an error will be thrown. 

Supported MIME Types: 


- PDF 
- Audio (MP3, MP4, WEBM) 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
