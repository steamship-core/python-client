#!/bin/bash
for file in $(find "../../python-docs/pages" -type f -name "index.md"); do
    # Get the directory path
    dir=$(dirname "$file")
    # Get the directory name
    dirname=$(basename "$dir")
    # Move and rename the file
    mv "$file" "${dir}.md"
done

# Rename root file
mv "../../python-docs/pages.md" "../../python-docs/pages/index.md"

# Delete all empty folders
find "../../python-docs/pages" -type d -empty -delete