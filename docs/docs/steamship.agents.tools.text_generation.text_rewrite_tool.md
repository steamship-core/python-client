<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/text_generation/text_rewrite_tool.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.tools.text_generation.text_rewrite_tool`




**Global Variables**
---------------
- **DEFAULT_PROMPT**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/text_generation/text_rewrite_tool.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TextRewritingTool`
Example tool to illustrate rewriting a statement according to a particular personality. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/text_generation/text_rewrite_tool.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```

Rewrites each provided text block using the stored prompt. Non-text blocks are passed through without modification. 

Inputs 
------ input: List[Block]  A list of blocks to be rewritten if they contain text. Each block will be considered a separate input. memory: AgentContext  The active AgentContext. 

Output 
------ output: List[Blocks]  A list of blocks whose content has been rewritten. Synchronously produced (for now). 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
