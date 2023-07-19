<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.lambda_handler`





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `encode_exception`

```python
encode_exception(obj)
```

When logging an exception ex: logging.exception(some_error), the exception must be turned into a string so that it is accepted by elasticsearch 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `internal_handler`

```python
internal_handler(
    invocable_cls_func: Callable[[], Type[Invocable]],
    event: Dict,
    client: Steamship,
    invocation_context: InvocationContext,
    call_instance_init: bool = False
) → InvocableResponse
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L121"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `handler`

```python
handler(
    bound_internal_handler,
    event: Dict,
    _: Dict = None,
    running_locally: bool = False
) → dict
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L248"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_custom_format`

```python
create_custom_format(
    invocation_context: InvocationContext,
    event: Dict
) → Callable[[LogRecord], Dict]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L280"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_handler`

```python
create_handler(invocable_cls: Type[Invocable])
```

Deprecated wrapper function for a Steamship invocable within an AWS Lambda function. Called by code within a plugin or package. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L296"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `safely_find_invocable_class`

```python
safely_find_invocable_class() → Type[Invocable]
```

Safely find the invocable class within invocable code. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L311"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_class_from_module`

```python
get_class_from_module(module) → Type[Invocable]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L332"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_safe_handler`

```python
create_safe_handler(known_invocable_for_testing: Type[Invocable] = None)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/lambda_handler.py#L340"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `<lambda>`

```python
<lambda>(event, context=None)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
