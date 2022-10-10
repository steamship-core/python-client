.. _blockifiers:

Blockifiers
-----------

Blockifiers convert data into Steamship’s native format.
All data imported into Steamship must be first blockified before it can be used.

-  A Blockifier’s input is raw bytes. Examples include a PDF, image,
   audio, HTML, CSV, JSON-formatted API output, or so on.
-  A Blockifier’s output is an object in Steamship’s native Block
   format.

You can use blockifiers when developing Steamship packages, in your own Python app code, or as one-off functions that
convert data in the cloud.

.. include:: ./using-blockifiers.rst
.. include:: ./developing-blockifiers.rst
