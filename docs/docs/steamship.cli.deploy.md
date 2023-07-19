<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.cli.deploy`




**Global Variables**
---------------
- **DEFAULT_BUILD_IGNORE**

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `update_config_template`

```python
update_config_template(manifest: Manifest)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_archive_path`

```python
get_archive_path(manifest: Manifest) → Path
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `bundle_deployable`

```python
bundle_deployable(manifest: Manifest)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `DeployableDeployer`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L134"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ask_for_new_handle`

```python
ask_for_new_handle(manifest: Manifest, was_missing: bool = False)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L178"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ask_for_new_version_handle`

```python
ask_for_new_version_handle(manifest: Manifest, was_missing: bool = False)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L93"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_object`

```python
create_object(client: Steamship, manifest: Manifest)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_or_fetch_deployable`

```python
create_or_fetch_deployable(client: Steamship, user: User, manifest: Manifest)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_version`

```python
create_version(client: Steamship, manifest: Manifest, thing_id: str)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deployable_type`

```python
deployable_type()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L97"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_object`

```python
update_object(deployable, client: Steamship, manifest: Manifest)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L207"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PackageDeployer`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L134"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ask_for_new_handle`

```python
ask_for_new_handle(manifest: Manifest, was_missing: bool = False)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L178"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ask_for_new_version_handle`

```python
ask_for_new_version_handle(manifest: Manifest, was_missing: bool = False)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L217"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_object`

```python
create_object(client: Steamship, manifest: Manifest)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_or_fetch_deployable`

```python
create_or_fetch_deployable(client: Steamship, user: User, manifest: Manifest)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_version`

```python
create_version(client: Steamship, manifest: Manifest, thing_id: str)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L232"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deployable_type`

```python
deployable_type()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L226"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_object`

```python
update_object(deployable, client: Steamship, manifest: Manifest)
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L236"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PluginDeployer`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L134"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ask_for_new_handle`

```python
ask_for_new_handle(manifest: Manifest, was_missing: bool = False)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L178"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ask_for_new_version_handle`

```python
ask_for_new_version_handle(manifest: Manifest, was_missing: bool = False)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L246"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_object`

```python
create_object(client: Steamship, manifest: Manifest)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_or_fetch_deployable`

```python
create_or_fetch_deployable(client: Steamship, user: User, manifest: Manifest)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_version`

```python
create_version(client: Steamship, manifest: Manifest, thing_id: str)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L263"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `deployable_type`

```python
deployable_type()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/cli/deploy.py#L257"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_object`

```python
update_object(deployable, client: Steamship, manifest: Manifest)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
