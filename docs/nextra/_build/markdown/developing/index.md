<a id="developingpackagesandplugins"></a>

# Developing Packages and Plugins

Think of Steamship packages and plugins as PyPi modules that run in the cloud.

- [Packages](../packages/index.md#packages) expose endpoints that can do work on an associated [workspace](../data/workspaces.md#workspaces)
- [Plugins](../plugins/index.md#plugins) conform to interfaces defined by the Steamship Engine to perform common tasks.

#### WARNING
Third-party plugin development is currently in Alpha and the interface may change.
If you want to build a plugin, we are eager to chat!
Just email [hello@steamship.com](mailto:hello@steamship.com) or hop on our [Discord](http://steamship.com/discord)

Steamship is designed from the ground up to support building, modifying, and sharing both packages and plugins.
Each one you create is cloned from an existing template of your choosing.
That template contains everything you need for a great development lifecycle:

1. A manifest file with metadata and statically-typed configuration
2. Unit tests with pre-configured GitHub Actions integration
3. Secrets management
4. A pre-written main body to build from
5. Simple deployment via the Steamship CLI and/or GitHub Actions

The process for  details are located in the following pages:

* [Cloning a Starter Project](project-creation.md)
* [The Steamship Manifest file](steamship-manifest.md)
* [Python Environment Setup](environment-setup.md)
* [Accepting Configuration](configuration.md)
* [Storing Secrets](storing-secrets.md)
* [Running on Localhost](running.md)
* [Writing Tests](testing.md)
* [Deploying](deploying.md)
* [Monitoring your Instances](monitoring.md)
