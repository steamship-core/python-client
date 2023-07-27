<a id="file-importers"></a>

# File Importers

File Importers import raw, unprocessed data into Steamship.

- A File Importer’s input is a URL or raw bytes.
- A File Importer’s output is raw bytes plus a MIME type.

You can use File Importers when developing Steamship packages, in your own Python app code, or as one-off functions that
import data in the cloud.

## Using File Importers

To use a [file importer](/importers/#file-importers), create an instance within your workspace and then refer to it when creating a file.

```python
# Load a Steamship Worksapce
from steamship import Steamship, File
client = Steamship(workspace="my-workspace-handle")

# Upload a file
importer = client.use_plugin("file-importer-handle", "instance-handle", config={})

# Create a file via that plugin instance.
file = File.create_with_plugin(client, plugin_instance=importer.handle)
```

The documentation for the file importer you use will provide instructions about how to pass required arguments to it.
Some require configuration (provided at plugin instance creation time) and others require a URL (provided at file creation time).
