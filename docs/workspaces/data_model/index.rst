.. _Data Model:

Workspace Data Model
--------------------

Workspaces have a managed data model that covers the 80% case of language AI.
It is simple, but flexible, and supports tasks as disparate as:

- file conversion
- text extraction
- classification
- text generation
- embedding search

There are only three core concepts you need to know.
**Files** are the top level object for storing data.
**Blocks** are regions of text within a file.
**Tags** are typed, key-valued assertions about a span of text.

.. toctree::
   :maxdepth: 2

   Files <files>
   Blocks <blocks>
   Tags <tags>
