<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/prompt_database_question_answerer.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.tools.question_answering.prompt_database_question_answerer`




**Global Variables**
---------------
- **DEFAULT_FACTS**
- **DEFAULT_QUESTION_ANSWERING_PROMPT**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/prompt_database_question_answerer.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PromptDatabaseQATool`
Example tool to illustrate how one can create a tool with a mini database embedded in a prompt. 

To use: 

 tool = PromptDatabaseQATool(  facts=[  "Sentence with fact 1",  "Sentence with fact 2"  ],  ai_description="Used to answer questions about SPECIFIC_THING. "  "The input is the question and the output is the answer."  ) 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/question_answering/prompt_database_question_answerer.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(facts: Optional[List[str]] = None, **kwargs)
```











---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
