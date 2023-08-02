.. _Clients:

Steamship Client Libraries
--------------------------

.. _Python Client:

Python Client
~~~~~~~~~~~~~

To install the Steamship Python Client, run:

.. code-block:: bash

   pip install steamship

Then, import and use Steamship with:

.. code-block:: python

   from steamship import Steamship

   ai_package = Steamship.use("package-name")

Most of this documentation site is Python-centric and will assume operation via that client.

.. _Typescript Client:

Typescript Client
~~~~~~~~~~~~~~~~~

.. warning::

   The Typescript client is alpha quality.

To install the Steamship Typescript Client, run:

.. code-block:: bash

   npm install --save @steamship/client

Then, import and use Steamship with:

.. code-block:: python

   import {Steamship, Workspace} from '@steamship/client'

   const client = new Steamship()
   const instance = await client.use("package")

Most of this documentation site is Python-centric and will assume operation via that client.
