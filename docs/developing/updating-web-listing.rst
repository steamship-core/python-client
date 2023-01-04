.. _UploadingWebListing:

Uploading your Web Listing
--------------------------

Steamship maintains a directory of public packages and plugins.
This directory gives each package author a place to link to and share.

The following information powers your project's web listing:

- The ``README.md`` file in your project folder
- The ``steamship.json`` file in your project folder

The ``README.md`` file is displayed as-is, and the ``steamship.json`` is parsed to generate links to demos, GitHub, and other locations.

Updating your Web Listing
~~~~~~~~~~~~~~~~~~~~~~~~~

Each time you  :ref:`Deploy via the Steamship CLI<Deploying>`, your web listing is updated.

You can also update it at any time with the following command:

.. code-block:: bash

   ship update

Adding taglines, demo links, and author icons
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A special JSON block called the ``steamshipRegistry`` in your ``steamship.json`` file contains several fields that will ehnahce your web listing.

Refer to :ref:`this page for a detailed outline<SteamshipOutline>`.
