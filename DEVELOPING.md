# NLUDB

The instructions below are only necessary for maintainers of this libary. 
For information about *using* this library, please see README.md

## Basic Information

* The project targets Python3
* The project is scaffolded via [PyScaffold](https://pyscaffold.org/)
* Testing is automated via [Tox](https://tox.readthedocs.io/en/latest/)

## Development Setup

Set up your virtual environment using the following commands:

```
cd $PROJECT_DIR
virtualenv .venv
source .venv/bin/activate
pip install -U pip setuptools setuptools_scm tox
pip install -e .
tox
```

## Testing

### Testing against NLUDB Production

1. **Set your NLUDB API Domain**. If you are using `nludb.com`, this step is not necessary. If you have a private NLUDB installation, use the API domain you normally use.

    ```
    export NLUDB_DOMAIN=http://api.nludb.yourcompany.com/
    ```

2. **Set your NLUDB API key**. For private NLUDB installations, we advise creating a dedicated test user.

    ```
    export NLUDB_KEY=(your key)
    ```

3. **Run the tests**. Below, `$PROJECT_DIR` is the location of the Python NLUDB Client repository on disk.

    ```
    cd $PROJECT_DIR
    source .venv/bin/activate
    tox
    ```
### Testing against NLUDB Development

Testing locally requires a few steps:

1. **Create a publicly accessible inbound proxy.** If using the cloud task scheduler, this will enable it to contact the NLUDB Engine on the local machine.

    ```
    ngrok http 8080
    ```

2. **Wire up the inbound proxy.** 

    In your `~/.nludb-config.json` file, set the `queueUrl` with the NGrok URL just generated.

    **You must use the https variant!**

    ```
      "queueUrl": "https://a5c6eb28c411.ngrok.io/...",
    ```

3. **Run the NLUDB Engine.** Await its availability on Port 8080.

4. **Run the steps for Production Testing**. See above.


## Deployment

```
git tag vXYZ
git push origin --tags
```
