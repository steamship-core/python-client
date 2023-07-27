<a id="data-model"></a>

# Data Model

There are only three core concepts you need to know.

1. [Files](files.md#files) are the top level object for storing data. A `File` can store raw data and an ordered list of `Blocks`.
2. [Blocks](blocks.md#blocks) are chunks of content within a `File`.  They can contain raw data and/or text, and an unordered set of `Tags`.
3. [Tags](tags.md#tags) are typed annotations on a `Block` or `File`.

The following diagram shows how data is created and used within Steamship:

![Lifecycle of a File](data/file-lifecycle.png)
1. File raw data can either be [created directly](files.md#creating-files-directly) or [imported via a File Importer](../plugins/using/importers/index.md#file-importers)
2. Blocks on Files can either be [created directly](blocks.md#creating-blocks) or [created from raw data by a Blockifier](../plugins/using/blockifiers/index.md#blockifiers)
3. Once you have blocks, you can run [Generators](../plugins/using/generators/index.md#generators) and [Taggers](../plugins/using/taggers/index.md#taggers)
4. Find data that you need by [querying](queries/index.md#queries)
5. Index data for search with [the embedding search index](../embedding-search/index.md#embedding-search-index)

* [Workspaces](workspaces.md)
* [Files](files.md)
* [Blocks](blocks.md)
* [Tags](tags.md)
* [Querying Data](queries/index.md)
