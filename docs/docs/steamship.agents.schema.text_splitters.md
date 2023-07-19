<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/text_splitters.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.schema.text_splitters`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/text_splitters.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TextSplitter`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/text_splitters.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `chunk_text_to_tags`

```python
chunk_text_to_tags(block: Block, kind: str, name: str = None) → List[Tag]
```

Split the incoming text into strings, and then wrap those strings in Tags 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/text_splitters.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `split_text`

```python
split_text(text: str) → List[str]
```

Split the incoming text into strings 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/text_splitters.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `FixedSizeTextSplitter`
Simplest possible chunking strategy; every n characters. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/text_splitters.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(chunk_size)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/text_splitters.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `chunk_text_to_tags`

```python
chunk_text_to_tags(block: Block, kind: str, name: str = None) → List[Tag]
```

Split the incoming text into strings, and then wrap those strings in Tags 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/text_splitters.py#L45"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `split_text`

```python
split_text(text: str) → List[str]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
