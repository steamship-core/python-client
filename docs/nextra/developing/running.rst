Running on Localhost
--------------------

To run your project on localhost type:

.. code-block:: bash

   ship run local

This will start a local instance with a number of ways to interact with it:

- A Console REPL, which will start immediately in the console.
- An HTTP endpoint, which will be printed to the console
- A Web endpoint, which will be printed to the console

The output will look like this:

.. code-block:: bash

   Running your project..

   🌎 Public API: https://example.ngrok.org/...
   🌎 Local API:  http://localhost:8080/...
   🌎 Web URL:    https://steamship:com/debug?https://...

   💬 Interactive REPL below.

   You: _

Localhost caveats
~~~~~~~~~~~~~~~~~

Running on localhost currently does not yet support asynchronous tasks.
In practice, this most often comes up with our ``DocumentIndexerPipelineMixin``, which enables loading in PDFs, YouTube videos, and other large documents for vector storage and retrieval.

