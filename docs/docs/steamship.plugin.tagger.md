<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/tagger.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.plugin.tagger`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/tagger.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Tagger`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/tagger.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    request: PluginRequest[BlockAndTagPluginInput]
) → InvocableResponse[BlockAndTagPluginOutput]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L31"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_endpoint`

```python
run_endpoint(**kwargs) → InvocableResponse[BlockAndTagPluginOutput]
```

Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/tagger.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TrainableTagger`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_training_parameters_endpoint`

```python
get_training_parameters_endpoint(
    **kwargs
) → InvocableResponse[TrainingParameterPluginOutput]
```

Exposes the Service's `get_training_parameters` operation to the Steamship Engine via the expected HTTP path POST /getTrainingParameters 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_endpoint`

```python
run_endpoint(**kwargs) → InvocableResponse[BlockAndTagPluginOutput]
```

Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/tagger.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_with_model`

```python
run_with_model(
    request: PluginRequest[BlockAndTagPluginInput],
    model: TrainableModel
) → InvocableResponse[BlockAndTagPluginOutput]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `train_endpoint`

```python
train_endpoint(**kwargs) → InvocableResponse[TrainPluginOutput]
```

Exposes the Service's `train` operation to the Steamship Engine via the expected HTTP path POST /train 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
