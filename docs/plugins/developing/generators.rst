.. _DevelopingGenerators:

Developing Generators
------------------
A ``Generator`` takes :ref:`Blocks` as input and creates new ``Blocks`` as output.

To implement a ``Generator``, your plugin class should inherit from :py:class:`steamship.plugin.generator.Generator`
and implement the abstract ``run`` method:

.. code-block:: python
   def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        input_blocks = request.data.blocks

        output_blocks = self.do_something_interesting(input_blocks)

        return InvocableResponse(data=RawBlockAndTagPluginOutput(blocks=output_blocks))


For example, an image ``Generator`` could merge the ``text`` from the input blocks and use it to generate an image ``Block``.

In addition to the input blocks and instance :ref:`configuration <Plugin Accepting Configuration>`, Generators can also receive
arbitrary key/value runtime parameters.  These are present in ``request.data.options``.

See `the DALL-E plugin <https://github.com/steamship-plugins/dall-e>`_ for a working example of a text to image ``Generator``.