.. _Packages:

Packages
========

Steamship Packages are full-lifecycle language AI libraries that run in the cloud.

Production language AI typically introduces significant operational complexity to a company:
piles of data, infrastructure, tasking, and integration must be managed alongside the "mere code" which
interfaces with the actual AI being used.
Steamship Packages solve this problem by encapsulating 100% of these concerns.

- A package's code is versioned and run in the cloud.
- A package's data is stored in a :ref:`workspace` specific to each instance
- A package's infrastructure is auto-managed from within each instance's workspace

This means that:

- Package authors can write and deploy packages using simple Python
- Package users can create as many package instances as they want, from any development environment
- Each instance is associated with an isolated, persistent data context and auto-managed cloud infrastructure

.. include:: ./using.rst

Developing new Packages
-----------------------

For those interested in developing packages, see :ref:`Developing Packages and Plugins`.