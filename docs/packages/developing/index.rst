Developing Packages
-------------------

Develop Steamship packages with our low-code Python stack and publish them for anyone to use.
It's the fastest way to build a full-lifecycle language AI service.

Here's how to go from zero-to-deployed in about 60 seconds.
Then you can customize your new package from there.

First, create a new package with our CLI:

.. code-block:: bash

   ship create

Then publish it

.. code-block:: python

   result = instance.invoke('method_name', arg1=val1, arg2=val2)


Both plugins and packages are designed to be regular Python objects that you can use and test locally,
but which can also be mounted by Steamship for running in the cloud.

In both cases, your implementation lives in the  ``src/api.py`` file of your project.
This file will have been created for you by the template you selected when starting your project.

- If you are developing a package, you will find a class that derives from the ``App`` base class
- If you are developing a plugin, you will find a class that derives from a base class specific to the plugin type.

In both cases, this ``src/api.py`` template concludes by setting a ``handler`` variable that is required by the Steamship bootloader for cloud operation.

The following sections contain a brief overview of the differences between package and plugin development.

.. include:: ./developing-packages.rst
.. include:: ./developing-plugins.rst
