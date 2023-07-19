<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/text_generation/json_object_generator.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.tools.text_generation.json_object_generator`




**Global Variables**
---------------
- **DEFAULT_PROMPT**
- **DEFAULT_PLURAL_OBJECT_DESCRIPTION**
- **DEFAULT_OBJECT_KEYS**
- **DEFAULT_OBJECT_EXAMPLES**
- **DEFAULT_NEW_ROW_PREFIX_FIELDS**


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/text_generation/json_object_generator.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `JsonObjectGeneratorTool`
Example tool to illustrate generating a new JSON object provided a set of examples. 

This is useful as an example of how to generate a new structured object: 


- A Person (e.g. name, gender, age) 
- A Proposed Podcast Episode (e.g. title, description, tags) 

The tool takes no input at runtime: it's a true generator parameterized only at initializtion time. 

The tool's parameterization is somewhat CSV-like in construction. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/text_generation/json_object_generator.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(*args, **kwargs)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/text_generation/json_object_generator.py#L86"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `kv_clause`

```python
kv_clause(key: str, value: str) → str
```

Return an escaped, JSON style key-value clause `"key": "value"` 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/text_generation/json_object_generator.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `object_json`

```python
object_json(schema: List[str], values: List[str])
```

Render a CSV-style header row and value list into a JSON object. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/tools/text_generation/json_object_generator.py#L100"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(
    tool_input: List[Block],
    context: AgentContext
) → Union[List[Block], Task[Any]]
```

Ignore tool input and generate a JSON object described by the tool's configuration. 

Inputs 
------ input: List[Block]  A list of blocks that will be ignored. memory: AgentContext  The active AgentContext. 

Output 
------ output: List[Blocks]  A single block containing a new row of the table described by the tool's configuration. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
