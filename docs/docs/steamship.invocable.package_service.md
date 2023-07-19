<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/package_service.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.package_service`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/package_service.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PackageService`
The Abstract Base Class of a Steamship Package. 

Packages may implement whatever methods they like.  To expose these methods as invocable HTTP routes, annotate the method with @get or @post and the route name. 

Package *implementations* are effectively stateless, though they will have stateful 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/package_service.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(*args, **kwargs)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/package_service.py#L99"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_mixin`

```python
add_mixin(
    mixin: 'PackageMixin',
    permit_overwrite_of_existing_methods: 'bool' = False
)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/package_service.py#L108"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `instance_init`

```python
instance_init()
```

The instance init method will be called ONCE by the engine when a new instance of a package or plugin has been created. By default, this calls instance_init on mixins, in order. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/package_service.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `invoke_later`

```python
invoke_later(
    method: 'str',
    verb: 'Verb' = <Verb.POST: 'POST'>,
    wait_on_tasks: 'List[Task]' = None,
    arguments: 'Dict[str, Any]' = None,
    delay_ms: 'Optional[int]' = None
) → Task[Any]
```

Schedule a method for future invocation. 

Parameters 
---------- method: str  The method to invoke, as registered with Steamship in the @get or @post decorator. verb:   Verb  The HTTP Verb to use. Default is POST. wait_on_tasks: List[Task]  A list of Task objects (or task IDs) that should be waited upon before invocation. arguments: Dict[str, Any]  The keyword arguments of the invoked method delay_ms: Optional[int]  A delay, in milliseconds, before the invocation should execute. 

Returns 
------- Task[Any]  A Task representing the future work 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/package_service.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `scan_mixin`

```python
scan_mixin(
    package_spec: 'PackageSpec',
    mixin_class: 'Type[PackageMixin]',
    mixin_instance: 'Optional[PackageMixin]' = None,
    permit_overwrite_of_existing_methods: 'bool' = False
)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
