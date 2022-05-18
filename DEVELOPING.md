# Steamship

We are excited to have you on board!

These instructions contain the setup for contributors fo the Steamship client library. 

For information about *using* this library, please see README.md

## Basic Information

* The project targets Python 3
* ✍️ Code formatting with black and isort
* ♻️ Continuous integration with GitHub Actions
* ✅ Code linting with pre-commit: bandit, darglint, flake8, mypy, pre-commit-hooks, pydocstyle, pygrep-hooks, pyupgrade, safety, and shellcheck
* Testing is automated via Pyunit
* 🧑‍💻 We recommend PyCharm as a development environment

## Development Setup

### Set up virtual environment

We highly recommend using virtual environments for development. 
Set up your virtual environment using the following commands:

```
cd $PROJECT_DIR
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.dev.txt
python -m pip install -e .
./bin/tox
```

This will install the required dependencies (runtime and development) and register the project source tree with your virtual environment so that `import steamship` statements will resolve correctly.

### Set up pre-commit-hooks

We use pre-commit hooks to validate coding standards before submission to code review. To make sure your code is always validated before each commit, please install the required git hook scripts as follows: 
```bash
pre-commit install
```

Once completed the pre-commit hooks wil run automatically on `git commit`. 

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

In general, each test should attempt to:

1. Create resources with randomized handles (to avoid collision).
2. Delete resources after test completion

## Deployment

To deploy a new version, use the GitHub Release feature to create a release and tag it `v#.#.#`.  

To release manually with only git & GitHub Actions, push a tag labeled `v#.#.#`:

```
git tag vX.Y.Z
git push origin --tags
```