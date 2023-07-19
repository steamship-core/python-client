<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.tools.base_tools`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `GeneratorTool`
A base class for tools that wrap Steamship Generator plugins. Subclass this and implement the `accept_output_block` method. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `accept_output_block`

```python
accept_output_block(block: Block) → bool
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_process`

```python
post_process(task: Task, context: AgentContext) → List[Block]
```

In this case, the Generator returns a GeneratorResponse that has a .blocks method on it 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L79"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ImageGeneratorTool`
A base class for tools that wrap Steamship Image Generator plugins. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `accept_output_block`

```python
accept_output_block(block: Block) → bool
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_process`

```python
post_process(task: Task, context: AgentContext) → List[Block]
```

In this case, the Generator returns a GeneratorResponse that has a .blocks method on it 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `VideoGeneratorTool`
A base class for tools that wrap Steamship Video Generator plugins. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L99"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `accept_output_block`

```python
accept_output_block(block: Block) → bool
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_process`

```python
post_process(task: Task, context: AgentContext) → List[Block]
```

In this case, the Generator returns a GeneratorResponse that has a .blocks method on it 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AudioGeneratorTool`
A base class for tools that wrap Steamship Audio Generator plugins. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `accept_output_block`

```python
accept_output_block(block: Block) → bool
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L71"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_process`

```python
post_process(task: Task, context: AgentContext) → List[Block]
```

In this case, the Generator returns a GeneratorResponse that has a .blocks method on it 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ScrapeAndBlockifyTool`
A base class for tools that wrap Steamship Blockifier plugin which transforms bytes to a set of blocks. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L128"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_mime_type`

```python
get_mime_type()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L171"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_process`

```python
post_process(task: Task, context: AgentContext) → List[Block]
```

In this case, the Blockifier returns a BlockAndTagResponse that has a .file.blocks method on it 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `should_blockify`

```python
should_blockify(block: Block) → bool
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L179"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ImageBlockifierTool`
A base class for tools that wrap Steamship Image Blockifier plugins. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L184"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_mime_type`

```python
get_mime_type()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L171"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_process`

```python
post_process(task: Task, context: AgentContext) → List[Block]
```

In this case, the Blockifier returns a BlockAndTagResponse that has a .file.blocks method on it 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L187"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `should_blockify`

```python
should_blockify(block: Block) → bool
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L191"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AudioBlockifierTool`
A base class for tools that wrap Steamship Audio Blockifier plugins. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_mime_type`

```python
get_mime_type()
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L171"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_process`

```python
post_process(task: Task, context: AgentContext) → List[Block]
```

In this case, the Blockifier returns a BlockAndTagResponse that has a .file.blocks method on it 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/base_tools.py#L199"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `should_blockify`

```python
should_blockify(block: Block) → bool
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
