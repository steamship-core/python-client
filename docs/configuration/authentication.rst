Authentication
--------------

Steamship uses API Keys to authenticate our CLI and client libraries.
These keys can be stored in a configuration file, in environment variables, or passed manually to our client libraries.

Steamship Configuration File
~~~~~~~~~~~~~~~~~~~~~

Logging in with the :ref:`Steamship CLI<CLI>` creates a configuration file at ``~/.steamship.json``.
This file contains your API Key, and our client libraries will auto-load information from this file when available.

It looks like this:

.. code-block:: json

   {
     "apiKey": "mykey"
   }

Using Multiple Profiles
~~~~~~~~~~~~~~~~~~~~~

The Steamship configuration file supports multiple profiles.
To create multiple profiles, use the following structure:

.. code-block:: json

   {
     "apiKey": "mykey",
     "profiles:" {
       "testing": {
         "apiKey": "test-key"
       },
       "work": {
         "apiKey": "work-key"
       }
     }
   }

When the ``STEAMSHIP_PROFILE`` environment variable is set, or when a ``profile`` argument is passed to a client library upon initialization, credentials will be loaded from that profile instead of the default.

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Our client libraries will prioritize loading credentials from the ``STEAMSHIP_KEY`` environment variable if it is present.


