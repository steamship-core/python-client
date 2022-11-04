.. _Blocks:

Blocks
~~~~~~

Blocks are ordered pages of text within a file.

They enable you to describe a portion of a file without describing the whole thing,
but they are otherwise free of meaning.

This means that different packages and plugins may choose divide files into blocks using different schemes.
Consider a CSV file uploaded to Steamship.
The following divisions of this file into blocks are all perfectly fine:

- Each CSV row is a block of text.
- Each 10 CSV rows is a block
- The entire CSV file is one block

All semantic information about that file's content --- such as row and column boundaries --- should be
provided via tags in the block.

Read the :py:class:`Block PyDoc spec here<steamship.data.block.Block>`.
