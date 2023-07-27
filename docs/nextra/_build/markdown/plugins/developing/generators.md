<a id="developinggenerators"></a>

# Developing Generators

A `Generator` takes [Blocks](../../data/blocks.md#blocks) as input and creates new `Blocks` as output.

To implement a `Generator`, your plugin class should inherit from [`steamship.plugin.generator.Generator`](../../api/steamship.plugin.md#steamship.plugin.generator.Generator)
and implement the abstract `run` method:

For example, an image `Generator` could merge the `text` from the input blocks and use it to generate an image `Block`.

In addition to the input blocks and instance configuration, Generators can also receive
arbitrary key/value runtime parameters.  These are present in `request.data.options`.

See [the DALL-E plugin](https://github.com/steamship-plugins/dall-e) for a working example of a text to image `Generator`.
