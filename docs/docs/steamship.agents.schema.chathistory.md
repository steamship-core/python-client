<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.schema.chathistory`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ChatHistory`
A ChatHistory is a wrapper of a File ideal for ongoing interactions between a user and a virtual assistant. It also includes vector-backed storage for similarity-based retrieval. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    file: 'File',
    embedding_index: 'Optional[EmbeddingIndexPluginInstance]',
    text_splitter: 'TextSplitter' = None
)
```

This init method is intended only for private use within the class. See `Chat.create()` 


---

#### <kbd>property</kbd> client





---

#### <kbd>property</kbd> initial_system_prompt





---

#### <kbd>property</kbd> last_agent_message





---

#### <kbd>property</kbd> last_system_message





---

#### <kbd>property</kbd> last_user_message





---

#### <kbd>property</kbd> messages





---

#### <kbd>property</kbd> tags







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L169"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `append_assistant_message`

```python
append_assistant_message(
    text: 'str' = None,
    tags: 'List[Tag]' = None,
    content: 'Union[str, bytes]' = None,
    url: 'Optional[str]' = None,
    mime_type: 'Optional[MimeTypes]' = None
) → Block
```

Append a new block to this with content provided by the agent, i.e., results from the assistant. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `append_message_with_role`

```python
append_message_with_role(
    text: 'str' = None,
    role: 'RoleTag' = <RoleTag.USER: 'user'>,
    tags: 'List[Tag]' = None,
    content: 'Union[str, bytes]' = None,
    url: 'Optional[str]' = None,
    mime_type: 'Optional[MimeTypes]' = None
) → Block
```

Append a new block to this with content provided by the end-user. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L158"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `append_system_message`

```python
append_system_message(
    text: 'str' = None,
    tags: 'List[Tag]' = None,
    content: 'Union[str, bytes]' = None,
    url: 'Optional[str]' = None,
    mime_type: 'Optional[MimeTypes]' = None
) → Block
```

Append a new block to this with content provided by the system, i.e., instructions to the assistant. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `append_user_message`

```python
append_user_message(
    text: 'str' = None,
    tags: 'List[Tag]' = None,
    content: 'Union[str, bytes]' = None,
    url: 'Optional[str]' = None,
    mime_type: 'Optional[MimeTypes]' = None
) → Block
```

Append a new block to this with content provided by the end-user. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L261"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clear`

```python
clear()
```

Deletes ALL messages from the ChatHistory (including system). 

NOTE: upon deletion, refresh() is called to ensure up-to-date history refs. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L234"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_messages`

```python
delete_messages(selector: 'MessageSelector')
```

Delete a set of selected messages from the ChatHistory. 

If `selector == None`, no messages will be deleted. 



**NOTES:**

> - upon deletion, refresh() is called to ensure up-to-date history refs. - causes a full re-index of chat history if the history is searchable. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_or_create`

```python
get_or_create(
    client: 'Steamship',
    context_keys: 'Dict[str, str]',
    tags: 'List[Tag]' = None,
    searchable: 'bool' = True
) → ChatHistory
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L231"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_searchable`

```python
is_searchable() → bool
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L208"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `refresh`

```python
refresh()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L226"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `search`

```python
search(text: 'str', k=None) → Task[SearchResults]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/chathistory.py#L223"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `select_messages`

```python
select_messages(selector: 'MessageSelector') → List[Block]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
