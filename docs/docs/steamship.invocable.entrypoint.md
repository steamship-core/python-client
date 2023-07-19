<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/entrypoint.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.invocable.entrypoint`
This class is necessary to be able to please the entrypoints of both localstack and AWS. 

If we set the entrypoint directly to steamship.invocable.safe_handler (imported in the init from lambda_handler), AWS is happy, but localstack is not because it tries to read steamship.invocable as a py file, not a module. 

If we set the entrypoint to steamship.invocable.lambda_handler.safe_handler, Localstack is happy, but AWS is not, because it tries to read lambda_handler first, which imports things from steamship.invocable, which imports things from lambda_handler. 

By adding this file which basically no-ops safe_handler into steamship.invocable.entrypoint.safe_handler, both are happy. 





---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
