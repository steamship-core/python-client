.. _Deploying:

Deploying
---------

Packages and plugins must be deployed before they can be used.

New versions of your project automatically become the “default” version when new instances are created.
Unless an instance specifically requests a version, this new default version will be used.



Deploying with the Steamship CLI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can deploy a package or plugin with the Steamship CLI with single command from
the project root (make sure your python environment is active):

.. code-block:: bash

   ship deploy

If you don't have a ``steamship.json`` yet, the deploy process will create one. After the command exits, wait a few minutes for your new infrastructure to be ready in the cloud.
New instances of your project will then be directed to the new version.

Deploying via GitHub Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each package and plugin project is created from a a template that has been pre-configured to
auto-deploy within GitHub Actions when certain situations occur.

Before you deploy, make sure the ``handle`` and ``version`` fields in your ``steamship.json`` file are set:

-  The ``handle`` property of ``steamship.json``
-  The ``version`` property of ``steamship.json``

Production deployments occur upon:

-  Pushes to ``main``
-  Pushes to SemVer-style tags, prefixed with ``v`` (``vA.B.C``)

Staging deployments occur upon:

-  Pushes to ``staging``

When pushing to a SemVer-style tag, the tag’s version must match the
version contained within ``steamship.json``. Note that while the GitHub
branch must start with ``v``, the version identifier in
``steamship.json`` should omit it.

When pushing to ``main`` or ``staging``, the version contained in
``steamship.json`` is used.

Automated Deployment Setup
^^^^^^^^^^^^^^^^^^^^^^^^^^

Automated deployments can only occur if you have set the following
GitHub secrets:

-  The ``STEAMSHIP_KEY`` GitHub repository secret
-  The ``STEAMSHIP_API_BASE`` GitHub repository secret (optional)
-  The ``STEAMSHIP_KEY_STAGING`` GitHub repository secret
-  The ``STEAMSHIP_API_BASE_STAGING`` GitHub repository secret
   (optional)

Setting the following variable will additionally trigger Slack
notifications upon automated deployments:

-  The ``STEAMSHIP_SLACK_DEPLOYMENT_WEBHOOK`` Slack notification webhook
   URL (optional)

Modifying or disabling automated deployments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Automated deployment is triggered by the GitHub Actions workflow in
``.github/workflows/deploy.yml``. This file, in turn, invokes the
``steamship-core/deploy-to-steamship@main`` action.

To modify or disable automated deployments, remove, comment out, or
modify that file.

Troubleshooting Deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The deployment fails because the version already exists
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This means the version specified in ``steamship.json`` has already been
registered with Steamship. Simply update the version in
``steamship.json`` to an identifier that has not yet been used.

The deployment fails because the tag does not match the manifest file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This means you have tried to push a branch with a semver-style tag (like
``v1.2.3``), resulting in a version deployment whose name must match
that tag without the ``v`` prefix (``1.2.3``). Make sure the version
field of ``steamship.json`` matches this string.

For example, if you are deploying branch ``v6.0.0``, the ``version``
field of your ``steamship.json`` file must be ``6.0.0``

The deployment fails with an authentication error
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you’re deploying from GitHub Actions, make sure you’re set your
``STEAMSHIP_KEY`` in your GitHub secrets. If you’re deploying from your
local machine, make sure you’ve authenticated with the Steamship CLI.