Quick Setup
-----------

If you’re sitting down to develop a plugin, here’s a list of steps to
get up and running quickly.

1. Clone a starter project

From the command line, run ``ship create``. Select ``Plugin``, select
the desired type of plugin, and then the starter project that most
closely resembles the one you’d like to create.

2. Select a handle

Plugin handles are unique across all users and Workspaces. They are how
other code will refer to your plugin.

Open the ``steamship.json`` manifest file and select a handle unique to
you. You will know if you’ve selected a valid handle because deployment
will fail if the handle selected already exists. Handles can only
consist of lower letters, numbers, and dashes ``like-this``.

3. Set up your virtual environment

We recommend using Python virtual environments for development. To set
one up, run the following command from your plugin's root directory:

.. code:: bash

   python3 -m venv .venv

Activate your virtual environment by running:

.. code:: bash

   source .venv/bin/activate

Your first time, install the required dependencies with:

.. code:: bash

   python -m pip install -r requirements.dev.txt
   python -m pip install -r requirements.txt

4. Verify you can run tests

From the command line, run ``pytest`` to verify that the tests included
with your starter project work.

5. Begin developing

Open the ``src/api.py`` file to develop your plugin.
This file will have been created for you by the plugin template you selected when starting your project.

You can think of this file similarly to a Flask app.
It looks and feels like a regular Python class: you can use it and unit test it as such.
But it also contains decorators which expose methods to the Steamship Engine when deployed.

For details about
developing specific types of plugins, see the documentation for that
specific plugin type:

- :ref:`Developing File Importers<../file_importers/developing>`
- :ref:`Developing Blockifiers<../blockifiers/developing>`
- :ref:`Developing Taggers<../taggers/developing>`
- :ref:`Developing Embedders<../embedders/developing>`
