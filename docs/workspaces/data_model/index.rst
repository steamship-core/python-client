.. _Data Model:

Data Model
----------

Workspaces have a managed data model that covers the 80% case of language AI.
The data model is simple, but flexible, and provides a common integration point for tasks as disparate as file conversion
to classification to text generation to embedding search.

There are only three core concepts you need to know:

- :ref:`Files` - The top level object for storing data
- :ref:`Blocks` - Ordered regions of text within a file.
- :ref:`Tags` - Typed key-valued commentary on the text within a block.

In addition to those core concepts, you can also create instances of plugins and packages to do things to or with your data.

.. include:: files.rst
.. include:: blocks.rst
.. include:: tags.rst
