.. _Creating Workspaces:

Creating Workspaces
-------------------

Workspaces are created (or resumed) when creating a new Steamship client.
In your client's constructor, specify the workspace you'd like.
If it doesn't exist, it will be created for you.

.. tab:: Python

    .. code-block:: python

       from steamship import Steamship

       client = Steamship(workspace="my-workspace-name")

.. tab:: Typescript

    .. code-block:: typescript

       import { Steamship } from "@steamship/client"

       const client = Steamship({workspace: "my-workspace-name"})

.. tab:: HTTP

    .. code-block:: bash

       curl \
           --header "Content-Type: application/json" \
           --header "Authorization: Bearer $STEAMSHIP_KEY" \
           --request POST \
           --data '{"handle":"your-handle", "fetchIfExist":true}' \
           https://api.steamship.com/api/v1/workspace/create


Every workspace-specific operation this client performs will now take part in that workspace.
This includes file uploads, plugin training, plugin inference, queries, and any infrastructure associated.

If you need to switch your workspace, you can either create a new client or type:

.. tab:: Python

    .. code-block:: python

       client.switch_workspace("new-workspace-name")

