Implementing Plugins and Packages
---------------------------------

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
