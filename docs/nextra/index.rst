import { Callout } from \'nextra/components\';

Steamship
=========

Steamship is an SDK and hosting platform for AI Agents and Tools.

**Follow our [Agent Guidebook](/agent-guidebook) for a complete tutorial.**  

Steamship in 30 seconds
-----------------------
- :ref:`Build Agents<Building Agents>` which run in the cloud.
- :ref:`Use Plugins<Using Plugins>` for common operations like generating text with GPT, converting a CSV to text, or generating an image from text. Steamship manages asynchronicity and retries.
- :ref:`Store data in Files, Blocks, and Tags <Data Model>`. This allows you to :ref:`query <Queries>` or :ref:`search <Embedding Search Index>` it later.
- :ref:`Deploy as a Package<Developing Packages>`, creating a scalable API for your front end.
- :ref:`Create as many instances of the Package<Creating Package Instances>` as you want, each with its own data.

The best way to start is to make a simple package:

## Start from our Multimodal Agent Template

Clone our starter repository:

.. code-block:: bash

   git clone https://github.com/steamship-core/multimodal-agent-starter

Create a virtual environment and install dependencies:

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate

   pip install -r requirements.txt
   pip install -r requirements.dev.txt

Then run:

.. code-block:: bash

   ship run local

<Callout emoji=\"⚠️\">
An ngrok account is required to run this command.
</Callout>

Now that you've interacted with your new agent, you're ready to start modifying it in :code:`src/api.py`.

See the **[Agent Guidebook](/agent-guidebook)** for details.

Contents
========

* [Agent Guidebook](agent-guidebook)
.. toctree::
   :maxdepth: 4

   Configuration <configuration/index>
   Agents <agents/index>
   Packages <packages/index>
   Plugins <plugins/index>
   Data <data/index>
   Embedding Search Index <embedding-search/index>
   Developer Reference <developing/index>
   License <license>
   Authors <authors>


.. _NPM: http://npmjs.com/
