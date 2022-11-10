Receiving Webhooks
~~~~~~~~~~~~~~~~~~

You can use your Steamship package to receive a webhooks other services:

- Accept data from Zapier
- Receive new messages from a customer service apps
- Register as a handler for a chat bot framework

Every Steamship package instance :ref:`provides an HTTP API<can-i-access-my-package-over-http>`,
so receiving webhooks with a package is easy.

**Step 1. Write a Package Method**

Here's an example of a package method called ``on_new_email``.
It is annotated with the ``@post`` annotation to register it as an ``HTTP POST`` endpoint, and it takes two keyword arguments.

.. code-block:: python

   class MyPackage(PackageService):
      @post("on_new_email")
      def on_new_email(self, sender: str = None, body: str = None) -> str:
         """Receive a webhook notification with a message from a user and save it to a new file."""
         File.create(
           self.client,
           tags=Tag.CreateRequest(kind="sender", name=sender),
           content=body
         )
         return "OK"


**Step 2. Deploy your package and create an instance**

Code packages themselves don't do anything.
To create your API, you have to first:

- :ref:`Deploy your package<Deploying>` with the Steamship CLI
- :ref:`Create an instance<UsingPackages>` with Python, Typescript, cURL, or the Steamship CLI

**Step 3. Determine your instance's Webhook URL**

When you create an instance of your package, its API is assigned a :ref:`Base URL<can-i-access-my-package-over-http>`.
Determine your instance's Base URL using the instructions on that linked page.
Then add the method name to get your instance's Webhook URL.

For example, if your instance's Base URL was:


.. code-block::

   https://{userHandle}.steamship.run/{workspaceHandle}/{instanceHandle}/

then the webhook URL given the ``on_new_email`` method above would be:

.. code-block::

   https://{userHandle}.steamship.run/{workspaceHandle}/{instanceHandle}/on_new_email

**Step 4. Configure your webhook provider

The service sending your webhook will need your Webhook URL.

Steamship webhooks have a few additional requirements:

- The ``Content-Type`` header should be ``application/json``
- The ``Authorization`` header should be ``Bearer {api-key}``, replacing ``{api-key}`` with your API Key
- The HTTP verb can be ``POST`` or ``GET`` depending on whether you used ``@post`` or ``@get`` to register the Steamship method
- HTTP POST bodies should be JSON-encoded
