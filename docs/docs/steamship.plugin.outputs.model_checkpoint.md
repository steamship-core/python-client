<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/model_checkpoint.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.plugin.outputs.model_checkpoint`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/model_checkpoint.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ModelCheckpoint`




<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/model_checkpoint.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    client: Steamship,
    parent_directory: Optional[Path] = None,
    handle: str = 'default',
    plugin_instance_id: str = None
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/model_checkpoint.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `archive_path_in_steamship`

```python
archive_path_in_steamship(as_handle: str = None) → str
```

Returns the path to the checkpoint archive on Steamship. 

On steamship, the checkpoint is archived in the Workspace's PluginInstance bucket as: `{plugin_instance_bucket}/{plugin_instance_id}/{checkpoint_handle}.zip` 

Here we only return the following path since the bucket is specified separately in the required Steamship API calls: `{plugin_instance_id}/{checkpoint_handle}.zip` 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/model_checkpoint.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `archive_path_on_disk`

```python
archive_path_on_disk() → Path
```

Returns the path to the checkpoint archive on disk. 

On disk, the model checkpoint is the folder:  `{parent_directory}/{checkpoint_handle}.zip` 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/model_checkpoint.py#L82"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `download_model_bundle`

```python
download_model_bundle() → Path
```

Download's the model from Steamship and unzips to `parent_directory` 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/model_checkpoint.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `folder_path_on_disk`

```python
folder_path_on_disk() → Path
```

Returns the path to this checkpoint on the local disk. 

On disk, the model checkpoint is the folder:  `{parent_directory}/{checkpoint_handle}/` 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/model_checkpoint.py#L123"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `upload_model_bundle`

```python
upload_model_bundle(set_as_default: bool = True)
```

Zips and uploads the Model to steamship 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
