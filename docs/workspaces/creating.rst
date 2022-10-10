.. _Creating Workspaces:

Creating Workspaces
-------------------

Workspaces are created (or resumed) when creating a new Steamship client.
In your client's constructor, specify the workspace you'd like.
If it doesn't exist, it will be created for you.

.. code:: python

   client = Steamship(workspace="my-workspace-name")

Every workspace-specific operation this client performs will now take part in that workspace.
This includes file uploads, plugin training, plugin inference, queries, and any infrastructure associated.

If you need to switch your workspace, you can either create a new client or type:

.. code:: python

   client.switch_workspace("new-workspace-name")

