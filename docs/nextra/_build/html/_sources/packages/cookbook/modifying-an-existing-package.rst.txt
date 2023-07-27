Modifying an Existing Package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may want to modify an existing package to:
 * Add a new method
 * Swap out a plugin
 * Add more specific business logic

You can do this easily in Steamship!

As an example, let's assume we want to change the `audio-markdown <https://github.com/steamship-packages/audio-markdown>`_
package to use Assembly's speech to text instead of Whisper. The goal of the package is to automatically convert
audio files to Markdown using specific spoken words to start and end elements.

First, fork the the package repository.

Change the package handle in ``steamship.json`` to a new unique value.  You should also update the ``steamshipRegistry`` section with your contact info.

.. code-block:: json

    {
        "type": "package",
        "handle": "audio-markdown-with-assembly", <-- new value
        ...
    }


Now we can edit the code to use a different transcription plugin.  In a package, ``src/api.py`` contains the
main implementation. Looking in this file, we see that it is using the Whisper speech to text blockifier:

.. code-block:: python

    BLOCKIFIER_HANDLE = "whisper-s2t-blockifier"


This handle is a reference to the plugin being used.  We also provide a `plugin <https://github.com/steamship-plugins/assemblyai-s2t-blockifier>`_ for transcription
via `AssemblyAI <assemblyai.com>`_.  Its handle is ``s2t-blockifier-default``.  If we replace the existing handle with this value,
our package will use the AssemblyAI plugin instead:

.. code-block:: python

    BLOCKIFIER_HANDLE = "s2t-blockifier-default"

That's it!  We can now deploy our new package using the Steamship CLI:

.. code-block:: bash

    ship deploy

and use it like any other package.

If we wanted to instead add functionality to the package, for example adding an RST output format,
we could add a new method to the package:

.. code-block:: python

    @post("get_rst")
    def get_rst(self, task_id: str):
        """Get the rst for a transcribed audio file based on task_id."""

        # implementation here