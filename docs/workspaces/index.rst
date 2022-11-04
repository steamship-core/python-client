.. _Workspaces:

Workspaces
==========

Steamship Workspaces manage the data, models, and infrastructure necessary for a language AI project.

Workspaces can be used in two ways:

1. **As a cloud environment for language AI projects.**
   You can use Workspaces on their own from Jupyter notebooks or your own application code.

2. **As the backing store to :ref:`Steamship Packages<Packages>`.**
   Each Steamship Package instance is bound to a Workspace, giving it an isolated environment to store state and model parameters.

The following sections cover the core lifecycle and data model of a Workspace.

.. toctree::
   :maxdepth: 2

   Creating Workspaces <creating>
   Importing Data <importing>
   Blockifying Data <blockifying>
   Workspace Data Model <data_model/index>
   Querying Data <queries/index>
