.. _Generators:

**********
Generators
**********

Generators create more :ref:`Blocks` (content) on a :ref:`File<Files>`.

Using Generators
----------------

To use a generator, create an instance within your workspace and then invoke it.

.. code-block:: python

   from steamship import Steamship, File
   client = Steamship(workspace="my-workspace-handle")

   # Create the generator instance
   generator = client.use_plugin('generator-handle')

   # Apply the generator to some text
   generator_task = generator.generate(text="some text")
   generator_task.wait()

   blocks = generator_task.output.blocks


Input
-----

There are several ways to specify input to a ``Generator``:

**Raw Text** You can pass raw text directly to a generator:

.. code-block:: python

   generator_task = generator.generate(text="some text")

**Blocks of an existing File** You can pass the generator a ``File`` id to work on, optionally passing a subset of blocks:

.. code-block:: python

   # Pass all the Blocks in the File
   generator_task = generator.generate(input_file_id=my_file.id)

   # Pass some of the Blocks in the File
   # in this example the second and third blocks (zero-indexed)
   generator_task = generator.generate(input_file_id=my_file.id, input_file_start_block_index=1, input_file_end_block_index=3)

   # Pass in specific blocks from the file
   # in this example the third and fifth (zero-indexed)
   generator_task = generator.generate(input_file_id=my_file.id, input_file_block_index_list=[2, 4])


**A query for existing Blocks** You can pass the generator a :ref:`query<Queries>` that will produce ``Blocks`` for the ``Generator``.

.. code-block:: python

   # Pass all the Blocks in the File
   generator_task = generator.generate(block_query='kind "some-relevant-tag-kind"')


**Public output** If you wish to make the output of the generation public (for example an image or audio file), you can pass ``make_output_public = True`` to the call to ``generate``.

Output
------

When you call ``generate`` on a file or via a ``PluginInstance``, the object that is returned is a ``Task``. You can ``wait()`` on
this task, or continue on to do other work.
The output to a ``generate`` operation is :ref:`Blocks`. You can always get these blocks from the output of the ``Task``:

.. code-block:: python

   # Apply the generator to some text
   generator_task = generator.generate(text="some text")
   generator_task.wait()

   blocks = generator_task.output.blocks

By default, this output is **not** saved to a ``File``.  If you wish the result to be persisted,
you can pass ``append_output_to_file=True`` to the call, and it will be persisted to a **new** ``File``:

.. code-block:: python

   # Apply the generator to some text
   generator_task = generator.generate(text="some text", append_output_to_file=True)
   generator_task.wait()

   blocks = generator_task.output.blocks
   new_file_id = blocks[0].file_id

If you want the output to be appended to an existing ``File``, just pass its id as well:

.. code-block:: python

   # Apply the generator to some text
   generator_task = generator.generate(text="some text", append_output_to_file=True, output_file_id=my_file.id)
   generator_task.wait()

   blocks = generator_task.output.blocks

   # if we refresh my_file, we will see new blocks
   my_file.refresh()


Steamship provides several Generators:

.. toctree::
   :maxdepth: 1

   DALL-E <dalle>
   GPT-4 <gpt4>

Other generators are available on the Steamship `plugins page <https://www.steamship.com/plugins?tab=Public>`_