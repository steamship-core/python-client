<a id="plugins"></a>

# Plugins

[Steamship Plugins](https://www.steamship.com/plugins) perform specific tasks related to AI.

- How to [use plugins](using/index.md#using-plugins)
- How to [develop plugins](developing/index.md#developingpluginssec)

Steamship supports the following types of plugins:

## File Importers

Importers pull raw data from common external sources into a [File](../data/files.md#files).

*Examples*: A YouTube video importer imports video content given a URL, A Notion importer imports a document from a Notion space.

- [Using File Importers](using/importers/index.md#file-importers)
- [Developing File Importers](developing/importers.md#developingfileimporters)

## Blockifiers

Blockifiers extract text and other content from raw data in a [File](../data/files.md#files) to [Blocks](../data/blocks.md#blocks).

*Examples*: Whisper speech to text turns an audio file into a text transcript, a PDF extractor could pull the text chunks and images from a PDF document.

- [Using Importers](using/blockifiers/index.md#blockifiers)
- [Developing Importers](developing/blockifiers.md#developingblockifierssec)

## Taggers

Taggers create [Tags](../data/tags.md#tags) (annotations) on [Files](../data/files.md#files) and [Blocks](../data/blocks.md#blocks).

*Examples*: A text classifier would attach a classification `Tag` to a `Block`, an image object recognizer would add `Tags` to a `Block` that identified known objects.

- [Using Taggers](using/taggers/index.md#taggers)
- [Developing Taggers](developing/taggers.md#developingtaggers)

## Generators

Generators create new content from existing content.

*Examples*: GPT4 creates more text based on the existing text in a conversation, DALL-E creates an image based on a description.

- [Using Generators](using/generators/index.md#generators)
- [Developing Taggers](developing/generators.md#developinggenerators)

## Embedders

Embedders convert content into a vector representation. This is primarily used in combination with Steamship’s built in :ref:<Embedding Search Index>.

*Examples*: Use OpenAI to embed sentences into vectors for search; embed images into vectors for search

- [Using Embedders](using/embedders/index.md#embedders)
- [Developing Embedders](developing/embedders.md#developingembedders)
