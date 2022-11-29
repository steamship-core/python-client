"""
This class is necessary to be able to please the entrypoints of both localstack and AWS.

If we set the entrypoint directly to steamship.invocable.safe_handler (imported in the init
from lambda_handler), AWS is happy, but localstack is not because it tries to read steamship.invocable as a py file,
not a module.

If we set the entrypoint to steamship.invocable.lambda_handler.safe_handler, Localstack is happy, but AWS
is not, because it tries to read lambda_handler first, which imports things from steamship.invocable, which imports
things from lambda_handler.

By adding this file which basically no-ops safe_handler into steamship.invocable.entrypoint.safe_handler, both are
happy.

"""

from steamship.invocable import safe_handler

_ = safe_handler  # No op line so that my "unused" import does not get removed.
