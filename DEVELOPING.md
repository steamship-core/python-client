# Steamship

We are excited to have you on board!

These instructions contain the setup for contributors to the Steamship client library. 

For information about *using* this library, please see README.md

## Basic Information

* 🐍 The project targets Python 3
* ✍️ Code formatting is performed with black and isort
* ♻️ Continuous integration is performed via GitHub Actions
* ✅ Code linting is automated via pre-commit hooks: bandit, darglint, flake8, mypy, pre-commit-hooks, pydocstyle, pygrep-hooks, pyupgrade, safety, and shellcheck
* 📋 Testing is automated via Pyunit
* 🧑‍💻 We recommend PyCharm as a development environment

## Development Setup

### Set up virtual environment

First make sure you have Python3.8 -- the officially supported version

We highly recommend using virtual environments for development. 
Set up your virtual environment using the following commands:

```
python3.8 -m venv .venv
source .venv/bin/activate
python3.8 -m pip install -r requirements.txt
python3.8 -m pip install -r requirements.dev.txt
```

This will install the required dependencies (runtime and development) and register the project source tree with your virtual environment so that `import steamship` statements will resolve correctly.

### Set up pre-commit-hooks

We use pre-commit hooks to validate coding standards before submission to code review. To make sure your code is always validated before each commit, please install the required git hook scripts as follows: 
```bash
pre-commit install
```

Once completed the pre-commit hooks wil run automatically on `git commit`. 

When pre-commit hooks make file modifications, the `git commit` command that triggered them will fail and need to be run again. Simply run the command multiple times until it succeeds.

You can run the pre-commit hooks manually via:
```bash
pre-commit run --all-files
```

### Set your IDE to use proper Docstrings

Steamship uses PyCharm for Python development. 

In PyCharm:

* Navigate to Preferences -> Tools -> Python Integrated Tools -> Docstring Format
* Select "NumPy" as the Docstring Format.

## Package Design

* `base` depends on nothing.
* `data` depends on `base`
* `plugin` depends on `base`, `data`
* `client` depends on `base`, `data`, `plugin`
* `app` depends on `base`, `data`, `plugin`, `client`

Developers who are:

* Using Steamship need `client`
* Writing a plugin need `plugin`
* Writing an app need `app`

## Testing

### Configuring Test Credentials

The tests include integration tests that are intended to be performed against a running Steamship server. They all execute by loading the `test` profile from your Steamship client configuration. 

To establish a `test` profile, edit your `~/.steamship.json` file to ensure it has the following:

```
{
  "profiles": {
    "test": {
        "apiKey": "YOUR-TEST-USER-KEY"
    }
  }
}
```

Steamship employees can test against a server running on localhost by adding the following `apiBase` and `appBase` arguments to your `test` profile:

```
{
  "profiles": {
    "test": {
      "apiBase": "http://localhost:8080/api/v1/",
      "appBase": "http://localhost:8081",
      "apiKey": "CHANGEME"
    },
}
```

### Testing Style

Many of the tests in this project are integration tests against a running, persistent version of Steamship, which means
that care must be taken to destroy the resources created by a test.

That can be done using the `client` fixture, which yields a Steamship client anchored in a new Space and then
deletes the space and all of its resources after the test has been run.

To use it, write your tests like this:

```python
from steamship.client import Steamship
from tests.utils.fixtures import client # noqa: F401

def test_e2e_corpus_export(client: Steamship):
    # You can use the provided client to create resources, and those resources
    # will be cleaned up after completion
    pass
```

Note that some resources do not live within a space:

* Apps
* App Versions
* Plugins
* Plugin Versions

As such, these resources will not be automatically cleaned up after the test, and your test must take care
to destroy them manually.

## Deployment

To deploy a new version, use the GitHub Release feature: 

1. Create a new tag using the semver format `#.#.#` (without the v)
2. Target `main` 
3. Click `Generate release notes` 
4. Click `Publich release` 
