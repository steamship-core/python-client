.. _DevelopingPackagesAndPlugins:

*******************************
Developing Packages and Plugins
*******************************

Think of Steamship packages and plugins as PyPi modules that run in the cloud.

-  :ref:`Packages` expose endpoints that can do work on an associated :ref:`workspace<Workspaces>`
-  :ref:`Plugins` conform to interfaces defined by the Steamship Engine to perform common tasks.

.. warning::
    Third-party plugin development is currently in Alpha and the interface may change.
    If you want to build a plugin, we are eager to chat!
    Just email hello@steamship.com

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
   Accepting Configuration <configuration>
   Storing Secrets <storing-secrets>
   Writing Tests <testing>
   Deploying <deploying>
   Updating your Web Listing <updating-web-listing>

