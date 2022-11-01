.. _CLI:

HTTP Operation
--------------

Our client library is designed to broker all communication to Steamship, but our API supports HTTP operation if desired.

Requests
~~~~~~~~

In general, most API requests consist of an HTTP ``POST`` with a JSON payload.
For such requests, make sure to set the ``Content-Type`` header as follows:

.. code-block:: bash

   Content-Type: application/json

Also include your API Key as a Bearer token in the header:

.. code-block:: bash

   Authorization: Bearer [YOUR TOKEN HERE]

Responses
~~~~~~~~~

All Steamship responses use the following JSON format over the wire.
Each field is optional.

.. code-block:: json

   {
     "data":any,
     "task": {
       "taskId":string,
       "taskState": "creating" | "waiting" | "running" | "succeeded" | "failed",
       "taskMessage": string,
       "taskCreatedOn": string,
       "taskLastModifiedOn":string
     }
   }

In this response structure:

- ``data`` contains the operation results, if available
- ``task`` contains the operation progress, if it is still underway or if it has failed.