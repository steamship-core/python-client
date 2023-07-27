Storing Secrets
---------------

You may wish your plugin instance to store secrets, such as an API key or random seed.
These should never be committed to your plugin's GitHub repository, but they can be easily bundled and loaded automatically during deployment.

Simply place your secrets in ``src/.steamship/secrets.toml`` and ensure that they are git-ignored.
All default plugin templates should have this file already git-ignored.
For example, your ``secrets.toml`` file might look like this:

.. code-block:: toml

   api_key = "be#45jdkjdsdfse3"
   random_seed = 12345

Steamship's plugin loader will automatically detect this file and attempt to set any properties on your plugin's
configuration object that have matching keys.

**Note:** Automated deployments via GitHub-actions will not have this git-ignored file.
To automate deployments that contain secrets, you will need to alter your GitHub Action scripts to create
these files using GitHub Secrets after the checkout but before the deployment.
