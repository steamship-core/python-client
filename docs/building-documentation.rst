### Building Documentation

The first time ever, run:

docker run -it --rm -v docs:/docs sphinxdoc/sphinx sphinx-quickstart

After that, run:

docker run --rm -v docs:/docs sphinxdoc/sphinx make html
