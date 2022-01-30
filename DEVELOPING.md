# Steamship

We are excited to have you on board!

These instructions contain the setup for contributors fo the Steamship client library. 

For information about *using* this library, please see README.md

## Basic Information

* The project targets Python3
* The project is scaffolded via [PyScaffold](https://pyscaffold.org/)
* Testing is automated via Pyunit
* We recommend VS Code as a development environment

## Development Setup

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

This project's unit tests are intended to be performed against a running Steamship server. They all execute by loading the `test` profile from your Steamship client configuration. 

To establish this profile, edit your `~/.steamship.json` file to ensure it has the following:

```
{
  "profiles": {
    "test": {
			"apiKey": "your-testuser-key"
    }
  }
}
```

For Steamship employees who may be testing against a server running on localhost, additionally add the following `apiBase` argument to your `test` profile:

```
{
  "profiles": {
    "test": {
			"apiKey": "your-testuser-key",
		  "apiBase": "http://localhost:8080/api/v1"
    }
  }
}
```

### Testing Style

In general, each test should attempt to:

1. Create resources with randomized handles (to avoid collision).
2. Delete resources after test completion

### Testing in VS Code

This project's configuration should result in automatic test availability for Visual Studio Code. 

1. Click on the chemistry beaker icon at left
2. Find the test you would like to run
3. Click either `Run` or `Run with Debug`

That's it: you should see the output in your editing window.

## Deployment

TODO: Document

```
git tag vXYZ
git push origin --tags
```
