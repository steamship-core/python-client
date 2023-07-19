<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/tool.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.schema.tool`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/tool.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AgentContext`
Placeholder to avoid circular dependency. 





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/tool.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Tool`
Tools provide functionality that may be used by `AgentServices`, as directed by `Agents`, to achieve a goal. 

Tools may be used to wrap Steamship packages and plugins, as well as third-party backend services, and even locally-contained bits of Python code. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/tool.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `as_openai_function`

```python
as_openai_function() → OpenAIFunction
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/tool.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `post_process`

```python
post_process(async_task: Task, context: AgentContext) → List[Block]
```

Transforms Task output into a List[Block]. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/tool.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```

Run the tool given the provided input and context. 

At the moment, only synchronous Tools (those that return List[Block]) are supported. 

Support for asynchronous Tools (those that return Task[Any]) will be added shortly. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
