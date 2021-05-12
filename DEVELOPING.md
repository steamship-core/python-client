# NLUDB

The instructions below are only necessary for maintainers of this libary. 
For information about *using* this library, please see README.md

## Basic Information

* The project targets Python3
* The project is scaffolded via [PyScaffold](https://pyscaffold.org/)
* Testing is automated via [Tox](https://tox.readthedocs.io/en/latest/)

## Setup

Set up your virtual environment using the following commands:

```
cd $PROJECT_DIR
virtualenv .venv
source .venv/bin/activate
pip install -U pip setuptools setuptools_scm tox
pip install -e .
tox
```

### Testing

```
cd $PROJECT_DIR
source .venv/bin/activate
export NLUDB_KEY=(your key)
tox
```


### Deploying


