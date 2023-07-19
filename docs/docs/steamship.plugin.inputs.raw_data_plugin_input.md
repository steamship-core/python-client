<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/inputs/raw_data_plugin_input.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.plugin.inputs.raw_data_plugin_input`




**Global Variables**
---------------
- **TEXT_MIME_TYPES**

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/inputs/raw_data_plugin_input.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_base64`

```python
is_base64(sb)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/inputs/raw_data_plugin_input.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RawDataPluginInput`
Input for a plugin that accepts raw data, plus a mime type. 

A plugin author need only ever concern themselves with two fields: 
- `data` - Raw bytes ` `default_mime_type` - The best guess as to `data`'s MIME Type unless otherwise known to be different. 

In practice, however, the lifecycle of this object involves a bit more under the hood: 


- **Potentially Base64 Decoding Data**. When decoding from a dict, the `data` field is assumed to be Base64 encoded.  This is to support JSON as a transport encoding over the wire. The constructor automatically performs the  decoding, and the Steamship Engine automatically performs the encoding, so the Plugin Author can mostly ignore  this fact. 


- **Potentially late-fetching the `data` from a `url`**. Some files are too large to comfortably send as Base64  within JSON. The Steamship Engine sometimes chooses to send an empty `data` field paired with a non-empty  `url` field. When this happens, the constructor proactively, synchronously fetches the contents of that `url`  and assigns it to the `data` field, throwing a SteamshipError if the fetch fails. Again, this is done  automatically so the Plugin Author can mostly ignore this fact. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/inputs/raw_data_plugin_input.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(**kwargs)
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
