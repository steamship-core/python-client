<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/generator.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.plugin.generator`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/generator.py#L29"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Generator`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/generator.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    request: PluginRequest[RawBlockAndTagPluginInput]
) → InvocableResponse[RawBlockAndTagPluginOutput]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_endpoint`

```python
run_endpoint(**kwargs) → InvocableResponse[RawBlockAndTagPluginOutput]
```

Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/generator.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `upload_block_content_to_signed_url`

```python
upload_block_content_to_signed_url(block: Block) → Block
```

Recreate the block (create request) as a URL request, rather than direct content, since we can't do a multipart file upload from here. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/generator.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TrainableGenerator`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L116"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_training_parameters_endpoint`

```python
get_training_parameters_endpoint(
    **kwargs
) → InvocableResponse[TrainingParameterPluginOutput]
```

Exposes the Service's `get_training_parameters` operation to the Steamship Engine via the expected HTTP path POST /getTrainingParameters 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_endpoint`

```python
run_endpoint(**kwargs) → InvocableResponse[RawBlockAndTagPluginOutput]
```

Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /generate 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/plugin/generator.py#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_with_model`

```python
run_with_model(
    request: PluginRequest[RawBlockAndTagPluginInput],
    model: TrainableModel
) → InvocableResponse[RawBlockAndTagPluginOutput]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `train_endpoint`

```python
train_endpoint(**kwargs) → InvocableResponse[TrainPluginOutput]
```

Exposes the Service's `train` operation to the Steamship Engine via the expected HTTP path POST /train 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
