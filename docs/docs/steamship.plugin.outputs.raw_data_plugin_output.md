<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/raw_data_plugin_output.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.plugin.outputs.raw_data_plugin_output`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/raw_data_plugin_output.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RawDataPluginOutput`
Represents mime-typed raw data (or a URL pointing to raw data) that can be returned to the engine. 

As a few examples, you can return: 
- Raw text: RawDataPluginOutput(string=raw_text, MimeTypes.TXT) 
- Markdown text: RawDataPluginOutput(string=markdown_text, MimeTypes.MKD) 
- A PNG image: RawDataPluginOutput(bytes=png_bytes, MimeTypes.PNG) 
- A JSON-serializable Dataclass: RawDataPluginOutput(json=dataclass, MimeTypes.JSON) 
- Steamship Blocks: RawDataPluginOutput(json=file, MimeTypes.STEAMSHIP_BLOCK_JSON) 
- Data uploaded to a pre-signed URL: RawDataPluginOutput(url=presigned_url, MimeTypes.TXT) 

The `data` field of this object will ALWAYS be Base64 encoded by the constructor. This ensures that the object is always trivially JSON-serializable over the wire, no matter what it contains. 

The `mimeType` field of this object should always be filled in if known. The Steamship Engine makes use of it to proactively select defaults for handling the data returned. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/raw_data_plugin_output.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    base64string: 'str' = None,
    string: 'str' = None,
    _bytes: 'Union[bytes, BytesIO]' = None,
    json: 'Any' = None,
    mime_type: 'str' = None,
    **kwargs
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/outputs/raw_data_plugin_output.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `parse_obj`

```python
parse_obj(obj: 'Any') → BaseModel
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
