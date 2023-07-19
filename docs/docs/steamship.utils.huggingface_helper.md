<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/huggingface_helper.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.utils.huggingface_helper`
This class is a helper for plugins to use models hosted on Hugging Face. 

It uses asyncio parallelism to make many http requests simultaneously. 


---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/utils/huggingface_helper.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_huggingface_results`

```python
get_huggingface_results(
    blocks: List[Block],
    hf_model_path: str,
    hf_bearer_token: str,
    additional_params: dict = None,
    timeout_seconds: int = 30,
    use_gpu: bool = False
) → List[list]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
