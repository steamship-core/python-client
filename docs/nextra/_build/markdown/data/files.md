<a id="files"></a>

# Files

Files are the top-level object for any piece of data in a workspace.

Files hold bytes of raw data (with a `mime_type`, and processed data in [Blocks](blocks.md#blocks).
A `File` may also have a list of [Tags](tags.md#tags) (annotations).

To do work on a `File`, it needs to be saved and its content must be in [Blocks](blocks.md#blocks).

There are a few ways to accomplish this:

- Create `File` and `Block` content directly (see below)
- Add raw data directly, then create `Blocks` with a [blockifier plugin](../plugins/using/blockifiers/index.md#blockifiers)
- Import raw data with a [File Importer](../plugins/using/importers/index.md#file-importers), then create `Blocks` with a [blockifier plugin](../plugins/using/blockifiers/index.md#blockifiers)

It’s useful to think of Steamship Files more broadly than “file on your desktop.”
They are any useful object:

- A conversation between a user and an assistant
- a PDF file
- a YouTube video
- a Podcast episode
- A Notion page
- the JSON representation of an AirTable API response

Read the [`File PyDoc spec here`](../api/steamship.data.md#steamship.data.file.File).

<a id="creating-files-directly"></a>

## Creating Files Directly

The quickest way to create data is to create Files with `Block` content directly:

```python
file = File.create(
   client=client,
   blocks=[Block(text="Some example text")]
)
```

<a id="public-files"></a>

## Making File Data Public

If you want the raw data bytes of a `File` to be publicly accessible, you can set the parameter `public_data = True` when calling `File.create()`.
This is useful if you wish to share a generated image or audio file, or must make the content viewable in a place that cannot
retain your Steamship API key.  You can also change the value of the `public_data` flag on an existing `File` by calling
`File.set_public_data`.
