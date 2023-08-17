# If you're having trouble building the documentation site on localhost, you can use this Dockerfile
# to build it.
#
# To do that:
#
# 1) Build this docker image from the docs/ folder of the project:
#
#      docker build . -t build-docs -f `pwd`/Dockerfile
#
# 2) Run this docker image from the ROOT FOLDER of the project:
#
#      docker run --rm -v `pwd`:/project build-docs

FROM sphinxdoc/sphinx
WORKDIR /project/docs
CMD ["make", "html"]