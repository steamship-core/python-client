Documentation Site Readme
=========================

Note: this file is `.txt` to avoid getting pulled into the actual docsite buildout :)

Building on Localhost
---------------------

This is the preferred, if you're writing a lot of docs, for speed:

First, from this directory:

```bash
pip install -r requirements.txt
```

Then:

```bash
make html
```

Finally:

```bash
open docs/_build/html/index.html
```

Building via Docker
--------------------

The first time ever, run:

docker run -it --rm -v docs:/docs --workdir /docs/docs sphinxdoc/sphinx sphinx-quickstart

From the project root, run:

docker run --rm -v `pwd`:/docs --workdir /docs/docs sphinxdoc/sphinx make html

After that, run:

docker run --rm -t -i -v `pwd`:/docs --workdir /docs/docs sphinxdoc/sphinx /bin/bash

RST Copy-Pastables
------------------

Headings
~~~~~~~~

RST assigns heading levels in the order it encounters them during processing.
We use the following mappings in this project:

```
H1 = with overline, for parts
H2 * with overline, for chapters
H3 -, for sections
H4 ~, for subsections
H5 ^, for subsubsections
H6 “, for paragraphs
```

Cards
~~~~~

.. grid::  2

   .. grid-item-card:: **Using Packages**
      :link: packages/using

      Header
      ^^^
      Card content
      +++
      Footer
