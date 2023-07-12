.. _HTTP:

HTTP Operation
--------------

Our client library is designed to broker all communication to Steamship,
but our API supports HTTP operation if desired.

Requests
~~~~~~~~

In general, most API requests consist of an HTTP ``POST`` with a JSON payload.
For such requests, make sure to set the ``Content-Type`` header as follows:

.. code-block:: bash

   Content-Type: application/json

Also include your API Key as a Bearer token in the header:

.. code-block:: bash

   Authorization: Bearer {your-token}

Optional Headers
^^^^^^^^^^^^^^^^

All API requests take place within the context of a :ref:`Workspace<Workspaces>`.
If you do not specify the workspace, you are using your ``default`` workspace.

To set the workspace in an API request, use the following header:

.. code-block:: bash

   X-Workspace-Handle: {your-workspace-handle}


Engine Response Format
^^^^^^^^^^^^^^^^^^^^^^

All Steamship Engine API responses use the following JSON format over the wire.
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

Creating a Package Instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Steamship packages are listed in our `package directory <https://www.steamship.com/packages>`_.
To create one, sent an HTTP post with the following information:

.. code-block::

   POST https://api.steamship.com/api/v1/package/instance/create
   {
     "packageHandle": "the-package-handle",
     "handle": "your-new-instance-handle",
     "packageVersionHandle: "optional-version-handle",
     "fetchIfExists": true,
     "config": {
       "key1": "value1"
     }
   }

In the above POST request, the **packageHandle** references the package you'd like to use.
The **handle** creates a private stack for data and infrastructure that package depends on.

The result will include a JSON object containing information about your new instance.

Invoking a Package Method
~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have a package instance, you can invoke a methods on it over HTTP.
Get the workspace handle and package instance handle from the response of your instance creation request.

.. code-block:: python

   POST https://{username}.steamship.run/{workspace-handle}/{instance-handle}/method
   {
     "JSON": "BODY"
   }

