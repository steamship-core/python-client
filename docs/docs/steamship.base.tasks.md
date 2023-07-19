<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.base.tasks`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CreateTaskCommentRequest`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ListTaskCommentRequest`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TaskComment`




<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(**kwargs)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L54"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create`

```python
create(
    client: 'Client',
    task_id: 'str' = None,
    external_id: 'str' = None,
    external_type: 'str' = None,
    external_group: 'str' = None,
    metadata: 'Any' = None
) → TaskComment
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete`

```python
delete() → TaskComment
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list`

```python
list(
    client: 'Client',
    task_id: 'str' = None,
    external_id: 'str' = None,
    external_type: 'str' = None,
    external_group: 'str' = None,
    page_size: 'Optional[int]' = None,
    page_token: 'Optional[str]' = None,
    sort_order: 'Optional[SortOrder]' = <SortOrder.DESC: 'DESC'>
) → TaskCommentList
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `parse_obj`

```python
parse_obj(obj: 'Any') → BaseModel
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TaskCommentList`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TaskState`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TaskType`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TaskRunRequest`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TaskStatusRequest`








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Task`
Encapsulates a unit of asynchronously performed work. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L212"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_comment`

```python
add_comment(
    external_id: 'str' = None,
    external_type: 'str' = None,
    external_group: 'str' = None,
    metadata: 'Any' = None
) → TaskComment
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L184"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `as_error`

```python
as_error() → SteamshipError
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L194"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get`

```python
get(client, _id: 'str' = None, handle: 'str' = None) → Task
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L189"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `parse_obj`

```python
parse_obj(obj: 'Any') → Task
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L228"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_update`

```python
post_update(fields: 'Set[str]' = None) → Task
```

Updates this task in the Steamship Engine. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L276"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `refresh`

```python
refresh()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update`

```python
update(other: 'Optional[Task]' = None)
```

Incorporates a `Task` into this object. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/base/tasks.py#L235"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `wait`

```python
wait(
    max_timeout_s: 'float' = 180,
    retry_delay_s: 'float' = 1,
    on_each_refresh: "'Optional[Callable[[int, float, Task], None]]'" = None
)
```

Polls and blocks until the task has succeeded or failed (or timeout reached). 

Parameters 
---------- max_timeout_s : int  Max timeout in seconds. Default: 180s. After this timeout, an exception will be thrown. retry_delay_s : float  Delay between status checks. Default: 1s. on_each_refresh : Optional[Callable[[int, float, Task], None]]  Optional call back you can get after each refresh is made, including success state refreshes.  The signature represents: (refresh #, total elapsed time, task) 

 WARNING: Do not pass a long-running function to this variable. It will block the update polling. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
