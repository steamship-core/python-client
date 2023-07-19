<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/vector_search_learner_tool.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.tools.question_answering.vector_search_learner_tool`
Answers questions with the assistance of a VectorSearch plugin. 



---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/vector_search_learner_tool.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `VectorSearchLearnerTool`
Tool to answer questions with the assistance of a vector search plugin. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/vector_search_learner_tool.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `learn_sentence`

```python
learn_sentence(
    sentence: str,
    context: AgentContext,
    metadata: Optional[dict] = None
)
```

Learns a sigle sentence-sized piece of text. 

GUIDANCE: No more than about a short sentence is a useful unit of embedding search & lookup. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/vector_search_learner_tool.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```

Learns a fact with the assistance of an Embedding Index plugin. 

Inputs 
------ tool_input: List[Block]  A list of blocks to be rewritten if text-containing. context: AgentContext  The active AgentContext. 

Output 
------ output: List[Blocks]  A lit of blocks containing the answers. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
