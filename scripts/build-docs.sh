#!/bin/bash
docker run --rm -v `pwd`:/docs --workdir /docs/docs sphinxdoc/sphinx make html