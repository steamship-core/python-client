.. _Using Plugins:

Using Plugins
=======

`Steamship Plugins <https://www.steamship.com/plugins>`_ perform specific tasks related to AI.

This page is about using existing plugins. If you want to develop a ``Plugin``, see :ref:`DevelopingPluginsSec`

Steamship supports the following types of plugins:


- :ref:`File Importers` pull raw data from common external sources into :ref:`Files`.
- :ref:`Blockifiers` extract text and other content from raw data from :ref:`Files` to :ref:`Blocks`.
- :ref:`Taggers` create :ref:`Tags` (annotations) on :ref:`Files` and :ref:`Blocks`.
- :ref:`Generators` create new :ref:`Blocks` (content) from existing :ref:`Blocks` (content).
- :ref:`Embedders` convert content into a vector representation. This is primarily used in combination with Steamship's built in Embedding Search.


.. _Creating Plugin Instances:

Plugin Instances
----------------

To use a ``Plugin``, create an instance of it. When building into a :ref:`Package<Packages>`, We recommend doing this in the constructor, and saving the result as a member
variable.

.. code-block:: python

    gpt4 = steamship.use_plugin("gpt-4")

``gpt4`` is now a ``PluginInstance``. The instance contains the plugin's configuration and is locked to the current version of the ``Plugin``.

To use a specific version of the ``Plugin``, pass the version handle:

.. code-block:: python

    gpt4 = steamship.use_plugin("gpt-4", version="0.0.1-rc.4")

To override default configuration parameters or provide required configuration values, pass a ``dict`` of values in the ``config`` parameter:

.. code-block:: python

    gpt4 = steamship.use_plugin("gpt-4", config={"max_tokens":1024})

To see available configuration parameters, check the documentation of the specific ``Plugin``.

To use a ``PluginInstance``, call the type-specific methods on it:

.. code-block:: python

    result_task = gpt4.generate(text="What's up GPT?")

Plugin invocations return asynchronous :ref:`Tasks` so that you can easily run many plugins and control when you need
the results.


See the plugin individual plugin types for further info on how each can be called.


Plugin FAQ
~~~~~~~~~~~

- :ref:`Can I access my plugin over HTTP?<can-i-access-my-plugin-over-http>`


.. _can-i-access-my-plugin-over-http:

Can I access my plugin over HTTP?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. While the preferred access pattern for plugins is via our SDK, Steamship does expose an HTTP API endpoint for plugin instance invocation.

The HTTP endpoint for plugin instance invocation is: ``https://api.steamship.com/api/v1/plugin/instance/{plugin-method}``.

Replace ``{plugin-method}`` with the name of the method you wish to invoke on your instance. For instance, for :ref:`Generators`, use ``generate`` and
for :ref:`Taggers`, use ``tag``.

Your HTTP call MUST use the following conventions:

- Set the ``Content-Type`` header to ``application/json``
- Set the ``Authorization`` header to ``Bearer {api-key}``, replacing ``{api-key}`` with your API Key
- Set one of the following headers:
   - ``X-Workspace-Id`` (to the workspace UUID for your workspace)
   - ``X-Workspace-Handle`` (to the workspace handle for your workspace)
- Default to ``HTTP POST`` if you're not sure which verb to use. The plugin documentation should specify.
- Add the arguments as a JSON-encoded POST Body
   - This MUST include a ``pluginInstance`` field set to the instance handle of your plugin.

For example, the HTTP equivalent of:

    .. code-block:: python

       gpt4.generate(text='Name three kinds of dogs')

would be:

    .. code-block::

       POST /api/v1/plugin/instance/generate
       Content-Type: application/json
       Authorization: Bearer {api-key}
       X-Workspace-Id: {workspace-id}

       {"appendOutputToFile": false, "text": "Name three kinds of dogs", "pluginInstance": "{plugin-instance-handle}"}


The HTTP call to a plugin will return JSON that includes a ``taskId``. For example:

    .. code-block:: json

       {
            "status": {
                "version": "1",
                "userId": "<redacted>",
                "input": "{\"appendOutputToFile\": false, \"text\": \"Name three kinds of dogs\", \"pluginInstance\": \"<redacted>\"}",
                "taskType": "internalApi",
                "taskId": "48025A24...F1CF",
                "workspaceId": "<redacted>",
                "taskCreatedOn": "2023-06-28T03:57:41Z",
                "name": "\/api\/v1\/plugin\/instance\/generate",
                "state": "waiting",
                "taskLastModifiedOn": "2023-06-28T03:57:41Z"
            }
        }


To retrieve the output, you can poll the Task via HTTP, using the Task status endpoint (``https://api.steamship.com/api/v1/task/status``):

   .. code-block::

       POST /api/v1/task/status
       Content-Type: application/json
       Authorization: Bearer {api-key}
       X-Workspace-Id: {workspace-id}

       {"taskId": "{task-id}"}


If the task has completed successfully, you will see something like:

   .. code-block:: json

        {
            "data": {
                "blocks": [{
                    "tags": [{
                        "kind": "role",
                        "name": "assistant"
                    }],
                    "text": "1. Labrador Retriever\n2. German Shepherd\n3. Beagle"
                }]
            },
            "status": {
                "input": "{\"appendOutputToFile\": false, \"text\": \"Name three kinds of dogs\", \"pluginInstance\": \"<redacted>\"}",
                "userId": "<redacted>",
                "taskLastModifiedOn": "2023-06-28T03:57:42Z",
                "taskType": "internalApi",
                "name": "\/api\/v1\/plugin\/instance\/generate",
                "state": "succeeded",
                "version": "1",
                "taskId": "48025A24...F1CF",
                "output": "{\"blocks\":[{\"tags\":[{\"name\":\"assistant\",\"kind\":\"role\"}],\"text\":\"1. Labrador Retriever\\n2. German Shepherd\\n3. Beagle\"}]}",
                "assignedWorker": "engine",
                "workspaceId": "<redacted>",
                "startedAt": "2023-06-28T03:57:41Z",
                "taskCreatedOn": "2023-06-28T03:57:41Z"
            }
        }


.. toctree::
   :hidden:

   File Importers <importers/index>
   Blockifiers <blockifiers/index>
   Taggers <taggers/index>
   Generators <generators/index>
   Embedders <embedders/index>
   Tasks <tasks>
