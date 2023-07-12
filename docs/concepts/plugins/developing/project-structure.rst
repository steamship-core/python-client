Plugin Project Structure
~~~~~~~~~~~~~~~~~~~~~~~~~

Your main implementation lives in the  ``src/api.py`` file of your project.
This file will have been created for you by the template you selected when starting your project.

Inside this file, you will find a class that derives from a base class specific to the plugin type.

From the implementation perspective, think of a plugin as a class that implements an Abstract Base Class that the Steamship Engine knows how to communicate with.
Each plugin type implements an abstract base class with a different contract.

Consider the following tagger plugin:

.. code-block:: python

   class TagFileTagger(Tagger):
    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> BlockAndTagPluginOutput:
        file = request.data.file
        file.tags.append(
          Tag.CreateRequest(kind="Demo", name="You've been tagged!")
        )
        return BlockAndTagPluginOutput(file=file)

Once deployed to Steamship, this plugin can be applied to files in Steamship, leaving each one with a tag that can be
queried later.

You can also :ref:`define configuration parameters<Accepting Configuration>` for your plugin.