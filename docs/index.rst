Steamship
=========

Welcome to Steamship -- the fastest way to ship Language AI in your software.

The best way to get started is by trying out a :ref:`package<Packages>`.
Steamship packages provide full-lifecycle language AI

First, install our CLI with the following terminal command (you'll need `NPM`_):

.. code:: bash

   npm install -g @steamship/cli

Next, select a Steamship :ref:`package<Packages>` to try with:

.. code:: bash

   ship try

You'll be guided through a menu than will copy down a Jupyter Notebook demo for you to explore.

Ready to develop your own? Just type:

.. code:: bash

   ship create

And select one of the package templates.

..
    TODO: Carry an example through to Package API calls
    TODO: Theme site to Steamship branding

Contents
========

.. toctree::
   :maxdepth: 2

   Authentication <authentication>
   Packages <packages/index>
   Plugins <plugins/index>
   Workspaces <workspaces/index>
   HTTP Operation <http_operation>
   Developing <developing/index>
   Python Client Reference <api/modules>
   License <license>
   Authors <authors>


.. _NPM: http://npmjs.com/
