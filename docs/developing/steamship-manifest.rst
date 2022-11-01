.. _Steamship Manifest Files:

Steamship Manifest Files
------------------------

Every Steamship package and plugin has a ``steamship.json`` file at its
root that describes the project to Steamship.

At a minimum, when you create a new project, you should fill out the following fields:

- ``handle``
- ``description``
- ``version``
- ``public``

Plugin and package handles are globally unique across Steamship.
They are how other code will refer to your project when using it.

The full list of fields is:

-  ``type`` - Either ``package`` or ``plugin``. Tells Steamship how to
   interpret this project. A ``package`` is a user library that
   others import and use. It can define custom endpoints and do anything
   from process audio files to implement a calculator. A ``plugin`` is
   an extension to the Steamship Engine. Plugins follow a strict
   interface contract governed by their plugin type.
-  ``handle`` - A globally unique identifier for the package, consisting
   of lowercase letters, numbers, and dashes. This is the name by which
   you will refer to your package elsewhere in Steamship code.
-  ``version`` - The version of your project, in SemVer style (``X.Y.Z``
   or ``X.Y.Z-abc123``). By default, the last version you deploy is the
   default used when new instances are created, but users can always
   specify an older version.
-  ``public`` - Whether users other than you can see and use this
   project.
-  ``author`` - Your name and contact information.
-  ``description`` - A short, one sentence description of the project’s
   purpose.
-  ``plugin`` - Plugin-specific configuration. See :ref:`description here<Plugin Manifest Config>`.
-  ``configTemplate`` - A schema for the configuration your project requires . See :ref:`the configuration documentation<configTemplate Schema>` for details.

.. _Plugin Manifest Config:

Plugin Configuration
--------------------

If your project is a Plugin, its ``steamship.json`` file contains a
``plugin`` variable that defines further parameterization that is
specific to Plugins.

That configuration looks like this:

.. code-block:: json

   {
     "plugin": {
       "type": "tagger",
       "isTrainable": false
     }
   }

That code shows the following required settings:

-  ``type`` - Either ``fileImporter``, ``corpusImporter``,
   ``blockifier``, ``tagger``, ``embedder``, or ``exporter``
-  ``isTrainable`` - Whether the plugin can be trained.

A trainable plugin obligates it to implement a few extra methods as a
part of its contract with the Steamship Engine.