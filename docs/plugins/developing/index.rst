.. _developing_plugins:

******************
Developing Plugins
******************

Think of a plugin as a PyPi package that runs in the cloud. Plugins
conform to a specific interface that the Steamship Engine uses to
perform work.

Every Steamship plugin is created from an empty template that provides
everything you need for a great development lifecycle:

1. A Steamship Manifest contains information about what the plugin does.
2. Unit tests via ``pytest`` are pre-configured to run with GitHub
   Actions.
3. Your plugin’s main body is implemented atop a base class that defines
   abstract methods
4. Deployment can be done via the Steamship CLI or pre-configured GitHub
   Actions scripts

A quick setup and full details are located in the following pages:

.. toctree::
   :maxdepth: 1

   Quick Setup <quick-setup>
   Environment Setup <environment-setup>
   The Steamship Manifest <steamship-manifest>
   Writing Tests <testing>
   Writing Async Plugins <async-plugins>
   Deploying Plugins <deploying>

In addition, you will be helped by browsing the developer notes for the
specific type of plugin you are creating:

- :ref:`Developing File Importers<Developing File Importers>`
- :ref:`Developing Blockifiers<Developing Blockifiers>`
- :ref:`Developing Taggers<Developing Taggers>`
- :ref:`Developing Embedders<Developing Embedders>`
