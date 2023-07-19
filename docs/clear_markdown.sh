#!/bin/bash

# Delete all empty folders
find "../../python-docs/pages" -type d -empty -delete

# Delete all files that aren't named _meta.json
find "../../python-docs/pages" -type f ! -name "_meta.json" -delete