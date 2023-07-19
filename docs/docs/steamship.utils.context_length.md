<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/context_length.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.utils.context_length`





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/context_length.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `token_length`

```python
token_length(block: Block, tiktoken_encoder: str = 'p50k_base') → int
```

Calculate num tokens with tiktoken package. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/context_length.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `filter_blocks_for_prompt_length`

```python
filter_blocks_for_prompt_length(
    max_tokens: int,
    blocks: List[Block]
) → List[int]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
