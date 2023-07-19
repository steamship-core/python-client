<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/vector_search_qa_tool.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.tools.question_answering.vector_search_qa_tool`
Answers questions with the assistance of a VectorSearch plugin. 

**Global Variables**
---------------
- **DEFAULT_QUESTION_ANSWERING_PROMPT**
- **DEFAULT_SOURCE_DOCUMENT_PROMPT**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/vector_search_qa_tool.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `VectorSearchQATool`
Tool to answer questions with the assistance of a vector search plugin. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/vector_search_qa_tool.py#L40"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `answer_question`

```python
answer_question(question: str, context: AgentContext) → List[Block]
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/vector_search_qa_tool.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```

Answers questions with the assistance of an Embedding Index plugin. 

Inputs 
------ tool_input: List[Block]  A list of blocks to be rewritten if text-containing. context: AgentContext  The active AgentContext. 

Output 
------ output: List[Blocks]  A lit of blocks containing the answers. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
