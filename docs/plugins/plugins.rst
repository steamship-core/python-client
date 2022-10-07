Plugins
=======

Steamship Plugins help the Engine perform specific tasks related to
Language AI.

Each plugin is a stateless, Python-based microservice that runs in the
cloud and conforms to a strict interface and data model. Plugins may do
work themselves, or they may adapt work done by third-party services for
use with Steamship.

Steamship supports the following types of plugins:

-  **File Importers** Import data, as bytes, into Steamship.
-  **Blockifiers** - Convert data into Steamship Block Format for
   processing.
-  **Taggers** - Tag and classify data with new information.
-  **Embedders** - Convert data into vector representation.
-  **Exporters** - Export Steamship data into other formats.

Plugins are intended to be created rarely and used prolifically. For
example, one might create:

-  A **Notion File Importer Plugin** to import a Notion page as
   Notion-formatted JSON
-  A **Notion Blockifier** to convert Notion-formatted JSON into
   Steamship Block Format
-  A **OpenAI Embedder** to embed sentences to Vectors via GPT-3

Having created such plugins, anyone could use them to import, embed, and
perform question-answering queries over their data in Notion. If someone
were to create plugin for another embedding service, or another data
source, it could be mixed and matched with existing plugins as well. In
this way, Steamship plugins lets developers build packages across
different data and AI services without worrying about the details of
tasking, persistence, and integration.