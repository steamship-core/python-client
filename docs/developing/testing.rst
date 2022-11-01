.. _Testing:

Throw, Log, and Test!
---------------------

Steamship plugins execute remotely, automatically, and potentially at high-scale.
This makes it critical that you:

-  Throw detailed exceptions eagerly
-  Log liberally
-  Write unit tests

Every plugin template comes with a detailed logging and testing setup.

Logging
~~~~~~~

We recommend that you log liberally within your plugin code.
Use Python's default ``logging`` library.

.. code-block:: python

   import logging
   logging.info("Hi there!")

Throwing Errors
~~~~~~~~~~~~~~~

When something goes wrong in a plugin, the correct response is to throw a ``SteamshipError``.
This will result in an error message returned to the end-user.

.. code-block:: python

   from steamship import SteamshipError
   raise SteamshipError(
      message="Some error message",
      error=optional_wrapped_error
   )

Manual Testing
~~~~~~~~~~~~~~

Your plugin template comes with a ``test/`` folder that stores ``pytest`` tests. You can run them with:

.. code-block:: bash

   pytest

Many templates additionally contain a ``test_data/`` folder with data that is read in as part of testing.

On your local machine, any tests will run using the run using the ``STEAMSHIP_API_KEY`` environment variable, if available, or using the key specified in your user-global Steamship settings (``~/.steamship.json``).

Automated testing
~~~~~~~~~~~~~~~~~

Your plugin template comes configured to auto-test upon pull-requests to the ``main`` and ``staging`` branches.
Testing will also be performed as part of the :ref:`automated deployment<deploying>`.

* Failing tests are will block any automated deployments
* We recommend configuring your repository to block pull-request merges unless a passing test has been registered

Automated testing setup
^^^^^^^^^^^^^^^^^^^^^^^

Testing requires that you set a GitHub secret named ``steamship_key_test``. This secret will be used to set the ``STEAMSHIP_API_KEY`` environment variable during test running.

Modifying or removing automated testing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Automated tests are run from the GitHub workflow located in your plugin project at ``.github/workflows/test.yml``

