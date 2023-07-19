<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.base.package_spec`
Objects for recording and reporting upon the introspected interface of a Steamship Package. 



---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RouteConflictError`




<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(message: str, existing_method_spec: 'MethodSpec')
```









---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ArgSpec`
An argument passed to a method. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(name: str, parameter: Parameter)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `pprint`

```python
pprint(name_width: Optional[int] = None, prefix: str = '') → str
```

Returns a pretty printable representation of this argument. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MethodSpec`
A method, callable remotely, on an object. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L104"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(**kwargs)
```

Create a new instance, making sure the path is properly formatted. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clean_path`

```python
clean_path(path: str = '') → str
```

Ensure that the path always starts with /, and at minimum must be at least /. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L154"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clone`

```python
clone() → MethodSpec
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `from_class`

```python
from_class(
    cls: object,
    name: str,
    path: str = None,
    verb: Verb = <Verb.POST: 'POST'>,
    config: Dict[str, Union[str, bool, int, float]] = None,
    func_binding: Optional[str, Callable[, Any]] = None
)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L182"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_bound_function`

```python
get_bound_function(service_instance: Optional[Any]) → Optional[Callable[, Any]]
```

Get the bound method described by this spec. 

The `func_binding`, if a string, resolves to a function on the provided Invocable. Else is just a function. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L178"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_same_route_as`

```python
is_same_route_as(other: 'MethodSpec') → bool
```

Two methods are the same route if they share a path and verb. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `pprint`

```python
pprint(name_width: Optional[int] = None, prefix: str = '  ') → str
```

Returns a pretty printable representation of this method. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L229"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PackageSpec`
A package, representing a remotely instantiable service. 


---

#### <kbd>property</kbd> all_methods

Return a list of all methods mapped in this Package. 



---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L288"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_method`

```python
add_method(new_method: MethodSpec, permit_overwrite_of_existing: bool = False)
```

Add a method to the MethodSpec, overwriting the existing if it exists. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L344"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clone`

```python
clone() → PackageSpec
```

Return a copy-by-value clone of this PackageSpec. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L334"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `dict`

```python
dict(**kwargs) → dict
```

Return the dict representation of this object. 

Manually adds the `methods` computed field. Note that if we upgrade to Pydantic 2xx we can automatically include this via decorators. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L309"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_method`

```python
get_method(http_verb: str, http_path: str) → Optional[MethodSpec]
```

Matches the provided HTTP Verb and Path to registered methods. 

This is intended to be the single place where a provided (VERB, PATH) is mapped to a MethodSpec, such that if we eventually support path variables (/posts/:id/raw), it can be done within this function. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L282"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `import_parent_methods`

```python
import_parent_methods(parent: Optional[ForwardRef('PackageSpec')] = None)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/package_spec.py#L264"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `pprint`

```python
pprint(prefix: str = '  ') → str
```

Returns a pretty printable representation of this package. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
