.. _DevelopingAsync:

Writing Asynchronous Plugins
----------------------------

If a plugin method calls a third-party API that is asynchronous, then that plugin should
adopt an asynchronous conversation with the Steamship Engine.
The ``Request[InputType]`` and ``Response[OutputType]`` objects passed into and returned from plugin invocations contain
fields that make such an asynchronous conversation quick and easy.

Signaling an Asynchronous Response
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A synchronous plugin method response always returns either a raw object or a ``Response`` object
wrapping a raw object:

.. code-block:: python

   class SomePlugin:
      def run(request):
         return Response(data=some_object)

To make this response asynchronous, return a ``Response`` object with the ``status`` field set to a
running ``Task`` object:

.. code-block:: python

   class SomePlugin:
      def run(request):
         return Response(
             status=Task(
                state=TaskState.running,
                remote_status_input={}
             )
         )

That will cause the Steamship Engine to record the plugin's work as still ``RUNNING``. It will schedule repeated
inquiries -- at increasingly longer intervals -- to check on whether the plugin invocation has.

The ``remote_status_input`` object on the returned ``Task`` contains a Python ``dict`` that will be provided to the
plugin when this future check occurs.
It is the appropriate location to stash metadata about the async work in progress, such as a task ID received from a third-party API.

Detecting an Asynchronous Progress Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a plugin responds with an asyncronous task, the Engine will begin checking back for status updates.
The Engine performs these checks via the same endpoints used to initiate the work.
It is therefore important for asynchronous plugins to be able to distinguish between invocations requesting new work and invocations checking on existing work.

The ``Request`` object contains a boolean field named ``is_status_check`` that distinguishes async status requests from new work requests.
If this field is ``true``, the request is checking the status of prior work.
If this field is ``false``, the request is initiating new work.

In a fully synchronous plugin method, it is generally safe to ignore the ``is_status_check`` field,
but if a plugin method is asynchronous, you must take care to always check it, like so:

.. code-block:: python

    def run(
            self, request: PluginRequest[InputType]
    ) -> Union[OutputType, Response[OutputType]]:

       if request.is_status_check:
           return self.check_status(request)
        else:
           return self.initiate_work(request)

In the above code, the ``initiate_work`` method would return a ``Task`` in the running
state with a useful ``remote_status_input`` field, as follows:

.. code-block:: python

    def initiate_work(
            self, request: PluginRequest[InputType]
    ) -> Union[OutputType, Response[OutputType]]:

         remote_job_id = api_client.do_something(
           request.data.data
         )

         return Response(
             status=Task(
                state=TaskState.RUNNING,
                remote_status_input={
                  "remote_job_id": remote_job_id
                }
             )
         )

And then the ``check_status`` method would retrieve the ``remote_status_input`` to check
on the status of the remote work.
If the work remains in progress, it responds with a task in the running state, just as before.
If the work is complete, it responds with the raw data object or a ``Response`` object wrapping it.

.. code-block:: python

    def check_status(
            self, request: PluginRequest[InputType]
    ) -> Union[BlockAndTagPluginOutput, Response[OutputType]]:

         # Fetch the key we know we set when backgrounding the task.
         remote_job_id = request.remote_status_input.get("remote_job_id")

         if api_client.is_complete(remote_job_id):
            return Response(data=some_output_object)
         else:
            return Response(
                status=Task(
                   state=TaskState.RUNNING,
                   remote_status_input={
                     "remote_job_id": remote_job_id
                   }
                )
            )

Throwing errors from an asynchronous plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Errors can be thrown from an asynchronous plugin just as they would be from a synchronous plugin.
Just raise a ``SteamshipError`` and the Engine will set the task's state to ``TaskState.FAILED`` and record the error output.

.. code-block:: python

   from steamship import SteamshipError
   raise SteamshipError(
      message="Some error message",
      error=optional_wrapped_error
   )
