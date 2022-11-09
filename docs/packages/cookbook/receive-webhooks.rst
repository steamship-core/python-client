Receive Webhooks
~~~~~~~~~~~~~~~~

Packages run in the cloud, and each instance of a package hosts its own HTTP API.

You can use this API to receive webhooks as long as the webhook can be configured with authentication headers.

Here's an example of what that webhook might look like as a method in your package:

.. code-block:: python

    @post("webhook")
    def webhook(self, date: str = None, moon_phase: str = None):
        """Receive a webhook containing the `date` and `moon_phase`.

        Each instance of the this package will expose the API:

        https://{username}.steamship.run/{workspaceHandle}/{instanceHandle}/webhook

        In that URL:
          - {username} is the username of the package instance creator
          - {workspaceHandle} is the workspace

        """

        # implementation here