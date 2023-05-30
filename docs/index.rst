Steamship
=========

Steamship is the fastest way to add AI to your software.

Think of Steamship as both a package manager and package hosting for AI.
Each `Steamship package <https://www.steamship.com/packages>`_ runs in the cloud on a managed stack.


Steamship in 30 seconds
-----------------------
- :ref:`Build Agents<Building Agents>` which run in the cloud.
- :ref:`Use Plugins<Using Plugins>` for common operations like generating text with GPT, converting a CSV to text, or generating an image from text. Steamship manages asynchronicity and retries.
- :ref:`Store data in Files, Blocks, and Tags <Data Model>`. This allows you to :ref:`query <Queries>` or :ref:`search <Embedding Search Index>` it later.
- :ref:`Deploy as a Package<Developing Packages>`, creating a scalable API for your front end.
- :ref:`Create as many instances of the Package<Creating Package Instances>` as you want, each with its own data.

The best way to start is to make a simple package:

Start from a template
---------------------

Clone one of our starter packages (https://github.com/steamship-packages):

.. code-block:: bash

   git clone https://github.com/steamship-packages/empty-package.git


Create a virtual environment and install dependencies:

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate

   pip install -r requirements.txt
   pip install -r requirements.dev.txt

and start editing ``src/api.py``.

Start from scratch
------------------
First, install our SDK and CLI (ideally in a virtual environment):

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate

   pip install steamship

Now copy this into ``api.py``:

.. code-block:: python

    from steamship.invocable import post, PackageService

    class MyPackage(PackageService):

        @post("hello_world")
        def hello_world(self, name: str = None) -> str:
            return f"Hello, {name}"

Next Steps
==========

.. grid::  1 1 2 3

   .. grid-item-card:: **Using Packages**
      :link: packages/using.html

      Use full-stack language AI packages in your own code.

   .. grid-item-card:: **Developing Packages**
      :link: packages/developing/index.html

      Build and deploy packages with our low-code framework.

   .. grid-item-card:: **Package Cookbook**
      :link: packages/cookbook/index.html

      Package examples for common scenarios.


Contents
========

.. toctree::
   :maxdepth: 4

   Configuration <configuration/index>
   Agents <agents/index>
   Packages <packages/index>
   Plugins <plugins/index>
   Data <data/index>
   Embedding Search Index <embedding-search/index>
   Developer Reference <developing/index>
   Python Client Reference <api/modules>
   License <license>
   Authors <authors>


.. _NPM: http://npmjs.com/
