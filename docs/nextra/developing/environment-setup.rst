Environment Setup
-----------------

Steamship plugins are written in Python.
We've standardized on ``venv`` for dependency management,
and every plugin starter template comes with a ``requirements.txt`` and ``requirements.dev.txt`` file describing
its dependencies.

If you add new dependencies as you develop, it is important that you add them to ``requirements.txt``.
Otherwise they will not be available when you deploy your plugin to the cloud.

To set up your virtual environment for the first time, run this command from your plugin's root directory:

.. code-block:: bash

   python3 -m venv .venv

You can activate your virtual environment by running:

.. code-block:: bash

   source .venv/bin/activate

Your first time, or any time you add a dependency, run:

.. code-block:: bash

   python -m pip install -r requirements.dev.txt
   python -m pip install -r requirements.txt

