.. _Blocks:

Blocks
~~~~~~

We encourage you to think of Steamship's ``Block`` object as a necessary unit of data
paging, but otherwise completely free of meaning.
That it so say: it is useful to have some way to break a very large file into chunks
in order to optimnize processing and network traffic. But those chunks are considered
an implementation detail with respect to the contents of the file.

Consider a UTF-8 encoded CSV file uploaded to Steamship.
It should not matter whether this file is represented as:

- One block per row
- One block per 10 rows
- One block for the whole file

All semantic information about that file --- such as row and column boundaries --- should be
provided via tags atop the data, not blocks.