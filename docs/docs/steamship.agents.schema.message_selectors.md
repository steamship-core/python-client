<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.schema.message_selectors`





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_user_message`

```python
is_user_message(block: Block) → bool
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `is_assistant_message`

```python
is_assistant_message(block: Block) → bool
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `tokens`

```python
tokens(block: Block) → int
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MessageSelector`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_messages`

```python
get_messages(messages: List[Block]) → List[Block]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `NoMessages`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_messages`

```python
get_messages(messages: List[Block]) → List[Block]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `MessageWindowMessageSelector`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_messages`

```python
get_messages(messages: List[Block]) → List[Block]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TokenWindowMessageSelector`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/message_selectors.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_messages`

```python
get_messages(messages: List[Block]) → List[Block]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
