.. _Plugins:

Plugins
=======

`Steamship Plugins <https://www.steamship.com/plugins>`_ perform specific tasks related to AI.

- How to :ref:`use plugins <Using Plugins>`
- How to :ref:`develop plugins <DevelopingPluginsSec>`

Steamship supports the following types of plugins:

File Importers
---------
Importers pull raw data from common external sources into a :ref:`File <Files>`.

*Examples*: A YouTube video importer imports video content given a URL, A Notion importer imports a document from a Notion space.

- :ref:`Using File Importers<File Importers>`
- :ref:`Developing File Importers<DevelopingFileImporters>`

Blockifiers
-----------
Blockifiers extract text and other content from raw data in a :ref:`File <Files>` to :ref:`Blocks`.

*Examples*: Whisper speech to text turns an audio file into a text transcript, a PDF extractor could pull the text chunks and images from a PDF document.

- :ref:`Using Importers<Blockifiers>`
- :ref:`Developing Importers<DevelopingBlockifiersSec>`

Taggers
-------
Taggers create :ref:`Tags` (annotations) on :ref:`Files` and :ref:`Blocks`.

*Examples*: A text classifier would attach a classification ``Tag`` to a ``Block``, an image object recognizer would add ``Tags`` to a ``Block`` that identified known objects.

- :ref:`Using Taggers<Taggers>`
- :ref:`Developing Taggers<DevelopingTaggers>`

Generators
----------
Generators create new content from existing content.

*Examples*: GPT4 creates more text based on the existing text in a conversation, DALL-E creates an image based on a description.

- :ref:`Using Generators<Generators>`
- :ref:`Developing Taggers<DevelopingGenerators>`

Embedders
---------
Embedders convert content into a vector representation. This is primarily used in combination with Steamship's built in :ref:<Embedding Search Index>.

*Examples*: Use OpenAI to embed sentences into vectors for search; embed images into vectors for search

- :ref:`Using Embedders<Embedders>`
- :ref:`Developing Embedders<DevelopingEmbedders>`



.. toctree::
   :maxdepth: 3
   :hidden:

   Using Plugins <using/index>
   Developing Plugins <developing/index>

