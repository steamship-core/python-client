<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.plugin.trainable_model`




**Global Variables**
---------------
- **MODEL_CACHE**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TrainableModel`
Base class for trainable models. 

Trainable models are not plugins. They are a thin wrapper around the state of a model designed to be **used with** the Steamship plugin system. 

# State Management 

100% of a TrainableModel's state management should save to & read from a folder on disk via the methods `save_to_folder` and `load_from_folder`. 

# Remote Saving and Loading 

`TrainableModel` instances automatically save to a user's Workspace on Steamship via `save_remote` method. They can load themselves from a user's workspace via the `load_remote` method. 

When saving a model, the caller provides `handle`, such as "V1" or "epoch_23". This allows that particular checkpoint to be re-loaded. By default, every save operation also saves the model to the "default" checkpoint, overwriting it if it already existed. When a user loads a model without specifying a checkpoint, the "default" checkpoint will be used. 

# Data Scope 

A TrainableModel's data is saved & loaded with respect to 

1) The user's active Workspace, and 2) The provided Plugin Instance within that workspace. 

The active workspace is read from the Steamship client context, and the `plugin_instance_id` is supplied as a method argument on the `save_remote` and `load_remote` methods. 

This organization enables a user to have arbitrarily many trained model instances of the same type colocated within a Workspace. 

# Training 

A training job is fully parameterized by the `TrainPluginInput` object. 

# Result Reporting 

A training job's results are reported via the `TrainPluginOutput` object. These results include a reference to the `save_remote` output, but they do not include the model parameters themselves. For example, after training, one could write: 

``` archive_path_in_steamship = model.save_remote(..)```
``` output = TrainPluginOutput(archive_path_in_steamship=archive_path_in_steamship,```  ...  ) 

That output is the ultimate return object of the training process, but the Plugin that owns this model need not wait for synchronous completion to update the Steamship Engine with intermediate results. It can use the `Response.post_update` to proactively stream results back to the server. 

# Third-party / External Models 

This model class is a convenient wrapper for models running on third party systems (e.g. Google's AutoML). In such a case: 


- The `train` method would begin the job on the 3rd party system. 
- The `save_to_folder` method would write the Job ID and any other useful data to the checkpoint path 
- The `load_from_folder` method would read this Job ID from disk and obtain an authenticated client with the  third party system. 
- Any `run` method the implementer created would ferry back results fetched from the third-party system. 
- Any status reporting in TrainPluginOutput would ferry back status fetched from the third-party system. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `load_from_folder`

```python
load_from_folder(checkpoint_path: Path)
```

Load 100% of the state of this model to the provided path. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `load_from_local_checkpoint`

```python
load_from_local_checkpoint(checkpoint: ModelCheckpoint, config: ~ConfigType)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `load_remote`

```python
load_remote(
    client: Client,
    plugin_instance_id: str,
    checkpoint_handle: Optional[str] = None,
    use_cache: bool = True,
    model_parent_directory: Path = None,
    plugin_instance_config: ~ConfigType = None
)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `receive_config`

```python
receive_config(config: ~ConfigType)
```

Stores config from plugin instance, so it is accessible by model on load or train. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L167"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save_remote`

```python
save_remote(
    client: Client,
    plugin_instance_id: str,
    checkpoint_handle: Optional[str] = None,
    model_parent_directory: Path = None,
    set_as_default: bool = True
) → str
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L95"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save_to_folder`

```python
save_to_folder(checkpoint_path: Path)
```

Saves 100% of the state of this model to the provided path. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `train`

```python
train(
    input: PluginRequest[TrainPluginInput]
) → InvocableResponse[TrainPluginOutput]
```

Train or fine-tune the model, parameterized by the information in the TrainPluginInput object. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/trainable_model.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `train_status`

```python
train_status(
    input: PluginRequest[TrainPluginInput]
) → InvocableResponse[TrainPluginOutput]
```

Check on the status of an in-process training job, if it is running externally asynchronously. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
