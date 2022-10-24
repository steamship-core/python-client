.. _Packages:

Packages
========

Steamship Packages are full-lifecycle language AI libraries that you can use from any programming environment.

Packages bundle up everything you need -- from code, to models, to task queues, to data storage -- so that you
can just import them and use them.

- **Packages run in the cloud.**
  You interact with them using our client libraries or via HTTP APIs.
  Running them in the cloud enables Steamship to auto-manage the infrastructure each one requires.

- **Packages are stateful.**
  Each package instance you create manages its own configuration, data, and models.
  We call that unit of state a ":ref:`workspace<Workspaces>`".
  You can create as many as you want, and you can reload each one whenever you want.

- **Packages are written in Python and deployed via our CLI.**
  New packages are developed using our Python SDK and deployed using the ``ship`` command line utility.

.. include:: ./using.rst

Developing new Packages
-----------------------

For those interested in developing packages, see :ref:`Developing Packages and Plugins<DevelopingPackagesAndPlugins>`.