<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.invocable`
Please see https://docs.steamship.com/ for information about building a Steamship Package 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `make_registering_decorator`

```python
make_registering_decorator(decorator)
```

Returns a copy of foreignDecorator, which is identical in every way(*), except also appends a .decorator property to the callable it spits out. 

(*)We can be somewhat "hygienic", but newDecorator still isn't signature-preserving, i.e. you will not be able to get a runtime list of parameters. For that, you need hackish libraries...but in this case, the only argument is func, so it's not a big issue 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `endpoint`

```python
endpoint(verb: str = None, path: str = None, **kwargs)
```

By using ``kwargs`` we can tag the function with Any parameters. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get`

```python
get(path: str, **kwargs)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L85"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `post`

```python
post(path: str, **kwargs)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `find_route_methods`

```python
find_route_methods(on_class: Type) → List[RouteMethod]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `merge_routes_respecting_override`

```python
merge_routes_respecting_override(
    base_routes: List[RouteMethod],
    this_class_routes: List[RouteMethod]
) → List[RouteMethod]
```

Merge routes from base classes into the routes from this class. If this class already has verb/path combo, ignore the one from the superclass, since it has now been overridden. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L129"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `route_list_contains`

```python
route_list_contains(route_method: RouteMethod, routes: List[RouteMethod])
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L89"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RouteMethod`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Invocable`
A Steamship microservice. 

This model.py class: 

 1. Provide a pre-authenticated instance of the Steamship client  2. Provides a Lambda handler that routes to registered functions  3. Provides useful methods connecting functions to the router. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L150"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    client: Steamship = None,
    config: Dict[str, Any] = None,
    context: InvocationContext = None
)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L234"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_api_route`

```python
add_api_route(
    method_spec: MethodSpec,
    permit_overwrite_of_existing: bool = False
)
```

Add an API route to this Invocable instance. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L248"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `config_cls`

```python
config_cls() → Type[Config]
```

Returns the configuration object for the Invocable. 

By default, Steamship packages and plugins will not take any configuration. Steamship packages and plugins may declare a configuration object which extends from Config, if needed, as follows: 

class MyPackageOrPlugin:  class MyConfig(Config):  ... 

 @classmethod  def config_cls(cls):  return MyPackageOrPlugin.MyConfig 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L316"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `get_config_parameters`

```python
get_config_parameters() → Dict[str, ConfigParameter]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L244"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `instance_init`

```python
instance_init()
```

The instance init method will be called ONCE by the engine when a new instance of a package or plugin has been created. By default, this does nothing. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L230"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `invocable_instance_init`

```python
invocable_instance_init() → InvocableResponse
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
