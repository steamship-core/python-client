Steamship Manifest Files
------------------------

Every Steamship package and plugin has a ``steamship.json`` file at its
root that describes the project to Steamship.

This file has a number of fields.

-  ``type`` - Either ``app`` or ``plugin``. Tells Steamship how to
   interpret this project. An ``app`` (package) is a user library that
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

Config Templates
----------------

Your ``steamship.json`` file contains a ``configTemplate`` variable that
defines the parameterization of the Package or Plugin. This
configuration is provided upon each new instance creation, and it is
frozen and saved with your instance for reuse.

The value of the ``configTemplate`` block takes the following form:

.. code:: json

   {
     "configTemplate": {
       "param_name": {
         "type": "boolean",
         "description": "Whether something should be enabled..",
         "default": false
       },
       "param_name_2": {
         "type": "string",
         "description": "Some string parameter.",
       }

     }
   }

In the above code, you can see that the parameter name is the key of the
object, and details about that parameter are in the associated body.
Those details are:

-  ``type`` - Either ``boolean``, ``string``, or ``number``.
-  ``description`` - A short description of the parameter.
-  ``default`` A default value if the user does not provide one.

If a parameter does not have a default value, and a Steamship user tries
to create a new instance without specifying it, that instance creation
will fail.

Plugin Configuration
--------------------

If your project is a Plugin, its ``steamship.json`` file contains a
``plugin`` variable that defines further parameterization that is
specific to Plugins.

That configuration looks like this:

.. code:: json

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