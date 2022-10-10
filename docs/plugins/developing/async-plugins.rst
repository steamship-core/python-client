Asynchronous Plugins
~~~~~~~~~~~~~~~~~~~~

If a plugin method calls a third-party API that is asynchronous, then you should implement that method
asynchronously as well.

The ``Request`` and ``Response`` objects passed into plugin method invocations contain
fields which make an asynchronous conversation with the Steamship Engine quick and easy.

A synchronous plugin method response always looks like the following:

.. code:: python

   return Response(data=some_object)

To make this asynchronous, return a task status object instead

.. code:: python

   return Response(status=Task(
       state=TaskState.RUNNING,
       TODO
   ))

That will cause the Steamship Engine to record the plugin's work as still ``RUNNING`` and schedule repeated
inquiries as to whether it has completed.

Of course, now you must be prepared to detect and respond to those inquiries. You can do this via the
``is_status_check`` field on the ``Request`` object. In a synchronous plugin method, it is generally safe
to ignore this field, but if a plugin method is asynchronous, you must take care to always check it.

.. code:: python

    def run(
            self, request: PluginRequest[RawDataPluginInput]
    ) -> Union[BlockAndTagPluginOutput, Response[BlockAndTagPluginOutput]]:

        if request.is_status_check:
            # The engine is checking on a plugin request that we previously reported as
            # running and still in progress!

            # We should load the remote_status_input object which stores state we can
            # use to identify and check on the work.
            input = request.status.remote_status_input

            # After checking, we either return a synchronous style response (if it's done)
            # or another async-style result (if it's still in progress)
        else:
            # The engine is requesting a new job! We should schedule the async work and
            # return that it's running
            return Response(status=Task(
                state=TaskState.RUNNING,
                remote_status_input={"remote_task_id": "abc-123"}
            ))


Asynchronous Plugin Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's how to do it.

First, let's imagine we have a third-party API that has three methods: one to start a long-running job,
one to check its status, and one to get the results.

.. code:: python

   class AsyncApi:
       def start_work(self) -> str
           return "job_id-1234"

       def is_complete(self) -> bool
           return False

       def get_result(self) -> bytes
           return b''

