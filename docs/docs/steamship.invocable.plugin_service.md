<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.plugin_service`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PluginService`
The Abstract Base Class of a Steamship Plugin. 

All Steamship Plugins implement the operation: 


- run(PluginRequest[T]) -> Response[U] 

Many plugins are effectively stateless. This run operation defines their entire capability. Examples of such stateless plugins are: 
- File Import Plugin 
- Export Plugin 

Other plugins have state but in a very controlled way: 
- they can be trained, 
- this trainable process produces a "model", 
- that model acts as the state on which the `run` method is conditioned 

This model is stored in the Steamship Workspace that owns the Plugin Instance, and access to it is provided by the hosting environment that runs the model. 
- TODO(ted) Document this process. 

These stateful plugins are called "Trainable Plugins," and they must implement the following additional methods: 


- get_training_parameters(PluginRequest[TrainingParameterInput]) -> Response[TrainingParameterOutput] 
- train(PluginRequest[TrainPluginInput]) -> Response[TrainPluginOutput] 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(request: 'PluginRequest[IN]') → Union[OUT, InvocableResponse[OUT]]
```

Runs the core operation implemented by this plugin: import, export, blockify, tag, etc. 

This is the method that a Steamship Plugin implements to perform its main work. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TrainablePluginService`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_training_parameters`

```python
get_training_parameters(
    request: 'PluginRequest[TrainingParameterPluginInput]'
) → InvocableResponse[TrainingParameterPluginOutput]
```

Produces the trainable parameters for this plugin. 

This method is run by the Steamship Engine prior to training to fetch hyperparameters. 


- The user themselves can provide hyperparameters on the TrainingParameterPluginInput object. 
- This method then transforms those into the TrainingParameterPluginOutput object, altering the user's values  if desired. 
- The Engine then takes those TrainingParameterPluginOutput and presents them on the TrainPluginInput 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `model_cls`

```python
model_cls() → Type[TrainableModel]
```

Returns the constructor of the TrainableModel this TrainablePluginService uses. 

This is required so the `run` method below can load the model and provide it to the subclass implementor. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(request: 'PluginRequest[IN]') → Union[OUT, InvocableResponse[OUT]]
```

Loads the trainable model before passing the request to the `run_with_model` handler on the subclass. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_with_model`

```python
run_with_model(
    request: 'PluginRequest[IN]',
    model: 'TrainableModel'
) → Union[OUT, InvocableResponse[OUT]]
```

Rather than implementing run(request), a TrainablePluginService implements run_with_model(request, model) 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L107"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `train`

```python
train(
    request: 'PluginRequest[TrainPluginInput]',
    model: 'TrainableModel'
) → InvocableResponse[TrainPluginOutput]
```

Train the model. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/plugin_service.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `train_status`

```python
train_status(
    request: 'PluginRequest[TrainPluginInput]',
    model: 'TrainableModel'
) → InvocableResponse[TrainPluginOutput]
```

Train the model. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
