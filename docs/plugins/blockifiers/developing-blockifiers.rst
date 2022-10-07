Developing
==========

Blockifier Plugins convert data into Steamship’s native format.

-  A Blockifier’s input is raw bytes that may contain a PDF, image,
   audio, HTML, CSV, API response, or so on.
-  A Blockifier’s output is an object in Steamship’s native Block
   format.

You can easily fork, customize, and `deploy <docs/DEPLOYING.md>`__ the
Blockifier Plugin in this project. Once you’ve deployed it, you can
`import and use it <docs/USING.md>`__ across your Workspaces and
Packages.

Project Setup
-------------

Think of this Blockifier Plugin as an NPM or PyPi package.

1. You maintain it in GitHub
2. You `unit test it <docs/TESTING.md>`__ locally or in your GitHub
   Actions pipeline
3. You describe it with a manifest file called ``steamship.json``
4. You `deploy it <docs/DEPLOYING.md>`__ to Steamship to make it
   available use by you and others
5. You [import and use it] (docs/USING.md) from other Steamship code

1. Selecting a Handle
~~~~~~~~~~~~~~~~~~~~~

Plugin handles are unique across all users and Workspaces. Think of them
like you think of an NPM or PyPi package name.

To customize and re-deploy this plugin as your own, edit the ``handle``
property of `steamship.json <steamship.json>`__ a new handle name. You
will know if you’ve selected a valid handle because deployment
(deployment)[docs/DEPLOYING.md] will fail if the handle selected already
exists.

Handles can only consist of lower letters, numbers, and dashes
``like-this``.

2. Set up your Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We recommend using Python virtual environments for development. To set
one up, run the following command from this directory:

.. code:: bash

   python3 -m venv .venv

Activate your virtual environment by running:

.. code:: bash

   source .venv/bin/activate

Your first time, install the required dependencies with:

.. code:: bash

   python -m pip install -r requirements.dev.txt
   python -m pip install -r requirements.txt

Developing Blockifiers
----------------------

All the code for this plugin is located in the ``src/api.py`` file.

Steamship plugins conform to standard base classes. You just have to
implement the main function that represents their contracts with the
server. The type of plugin is recorded in the ``type`` field of
`steamship.json <steamship.json>`__.

You can easily fork, customize, and republish this plugin with new
functionality.

This project is a **Blockifier** plugin. It’s contract is to take raw
bytes and produce Steamship Blocks – our internal format for describing
text and tags over that text. In Python, that contract looks like:

.. code:: python

       def run(self, request: PluginRequest[RawDataPluginInput]) -> Union[BlockAndTagPluginOutput]:
           pass

Throw, Log, and Test!
---------------------

Your plugin code will be executing (1) remotely, (2) automatically, and
(3) potentially at high-scale. This makes it critical that you:

-  Throw detailed exceptions eagerly
-  Log liberally
-  Write unit tests

See `TESTING.md <../../../TESTING.md>`__ for details on the
pre-configured testing setup.

Deploying
---------

To run this plugin on Steamship, you must first deploy it.

See `DEPLOYING.md <../../../DEPLOYING.md>`__ for instructions.