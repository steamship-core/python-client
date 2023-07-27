.. _Embedding Search Index:


Embedding Search Index
-----------------------
Steamship provides a built-in vector store and search interface. This can be used in
combination with a :ref:`Embedder <Embedders>` to quickly create a search over text, images,
or other content. To use the index, first create an instance of it with your preferred ``Embedder``
plugin (we recommend OpenAI):

.. code-block:: python

  index = steamship.use_plugin(
        "embedding-index",
        random_name(),
        config={"embedder":
            {
                "plugin_handle": "openai-embedder",
                "fetch_if_exists": True
            }
        }
    )

Once you've created the index and paired it with the embedder, Steamship will automatically vectorize
content as it is inserted and queried.

Inserting Data
--------------
The unit of insertion in a search index is :ref:``Tags``.  Embedding search is most useful on short-ish chunks
of text like sentences or short paragraphs. If your text or content is in ``Blocks``, you can create ``Tags``
over the spans that you wish to index and then insert them.

Querying Data
-------------
Once you've inserted content, you can query it using the ``query()`` method.
