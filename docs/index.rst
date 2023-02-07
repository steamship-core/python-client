Steamship
=========

Steamship is the fastest way to add Language AI to your software.

Think of us as a package manager for AI.
Each `Steamship package <https://www.steamship.com/packages>`_ runs in the cloud on a managed stack.
The best way to start is to make a simple package.

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
   Packages <packages/index>
   Plugins <plugins/index>
   Workspaces <workspaces/index>
   Developer Reference <developing/index>
   Python Client Reference <api/modules>
   License <license>
   Authors <authors>


.. _NPM: http://npmjs.com/
