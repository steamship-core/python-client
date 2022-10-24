.. _DevelopingPackagesAndPlugins:

*******************************
Developing Packages and Plugins
*******************************

Think of Steamship plugins and packages as a PyPi modules that run in the cloud.

-  :ref:`Packages` expose open-ended endpoints that can do work on an associated :ref:`workspace<Workspaces>`
-  :ref:`Plugins` conform to specific interfaces that the Steamship Engine uses to perform work.

..
    Should we note here that self-plugin development is in alpha right now?  It might be worth pointing out
    and asking them to contact us.

Steamship is designed from the ground up to support building, modifying, and sharing both packages and plugins.
Each one you create is cloned from an existing template of your choosing.
That template contains everything you need for a great development lifecycle:

1.  A manifest file with metadata and statically-typed configuration
2.  Unit tests with pre-configured GitHub Actions integration
3.  Secrets management
4.  A pre-written main body to build from
5.  Simple deployment via the Steamship CLI and/or GitHub Actions

The process for  details are located in the following pages:

.. toctree::
   :maxdepth: 1

   Cloning a Starter Project <project-creation>
   The Steamship Manifest file <steamship-manifest>
   Python Environment Setup <environment-setup>
   Implementing your Project <developing>
   Accepting Configuration <configuration>
   Storing Secrets <storing-secrets>
   Writing Tests <testing>
   Deploying <deploying>
