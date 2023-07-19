<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/action.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.schema.action`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/action.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Action`
Actions represent a binding of a Tool to the inputs supplied to the tool. 

Upon completion, the Action also contains the output of the Tool given the inputs. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/action.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_chat_messages`

```python
to_chat_messages() → List[Block]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/action.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AgentTool`







---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/action.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/action.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `FinishAction`
Represents a final selected action in an Agent Execution. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/action.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_chat_messages`

```python
to_chat_messages() → List[Block]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
