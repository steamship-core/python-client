Workspaces
==========

Steamship Workspaces encapsulate all the data,
infrastructure, and task management necessary for a langauge AI project.

Workspaces are typically used in the following way:

-  :ref:`Create a workspace<Creating Workspaces>` to isolate your data
-  :ref:`Upload data<Uploading data>` to your workspace
-  :ref:`Train or run plugins<Plugins>` on your data
-  :ref:`Query the results<Queries>`

Workspaces also encapsulate the state that backs Steamship Packages.
Each instance of a package runs within the context of a workspace --- usually one created specifically for that
package instance.

.. toctree::
   :maxdepth: 2

   Creating Workspaces <creating>
   Uploading Data <uploading>
   Data Model <data_model/index>
