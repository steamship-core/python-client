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
python3 -m venv .
source ./bin/activate
python -m pip install -U pip setuptools setuptools_scm tox
python -m pip install -e .
./bin/tox
```

## Deployment

```
git tag vXYZ
git push origin --tags
```
