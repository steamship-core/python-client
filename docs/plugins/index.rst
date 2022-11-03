.. _Plugins:

Plugins
=======

`Steamship Plugins <https://www.steamship.com/plugins>`_ perform specific tasks related to Language AI.

Each plugin is a stateless, Python-based microservice that runs in the
cloud and conforms to a strict interface and data model. Plugins may do
work themselves, or they may adapt work done by third-party services for
use with Steamship.

Steamship supports the following types of plugins:

.. toctree::
   :maxdepth: 1

   Importers <importers/index>
   Blockifiers <blockifiers/index>
   Taggers <taggers/index>
   Embedders <embedders/index>

Plugins are intended to be created rarely and used prolifically. For
example, one might create:

-  A **Notion File Importer Plugin** to import a Notion page as
   Notion-formatted JSON
-  A **Notion Blockifier** to convert Notion-formatted JSON into
   :ref:`Steamship Block format<Data Model>`
-  A **OpenAI Embedder** to embed sentences to Vectors via GPT-3

Having created such plugins, anyone could use them to import, embed, and
perform question-answering queries over their data in Notion. If someone
were to create plugin for another embedding service, or another data
source, it could be mixed and matched with existing plugins as well. In
this way, Steamship plugins lets developers build packages across
different data and AI services without worrying about the details of
tasking, persistence, and integration.

Additional Links
~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 3

   Developing Plugins <developing/index>

