<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/file_importer_mixin.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.mixins.file_importer_mixin`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/file_importer_mixin.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `FileImporterMixin`
Provide endpoints for easy file import -- both sync and async. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/file_importer_mixin.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(client: Steamship)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `import_text`

```python
import_text(text: str, mime_type: Optional[str]) → File
```

Import the text to a Steamship File. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `import_url`

```python
import_url(url: str) → File
```

Import the URL to a Steamship File. Actual import will be scheduled Async. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/mixins/file_importer_mixin.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `import_url_to_file_and_task`

```python
import_url_to_file_and_task(url: str) → Tuple[File, Optional[Task]]
```

Import the provided URL, returning the file and optional task, if async work is required. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
