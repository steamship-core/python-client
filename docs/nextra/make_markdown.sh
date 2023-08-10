#!/bin/bash
BUILDDIR="_build"
DOCSDIR="../../../steamship/apps/python-docs/pages"

# Ignore the auto generated api folder.
rm -rf "$BUILDDIR"/markdown/api

# Delete all files that aren't named _meta.json, _app.mdx, or within the api folder

# Use find to recursively iterate over files and directories
find "$DOCSDIR" -type f | while read -r file; do
    # Get the file's directory
    dir=$(dirname "$file")

    # If the file is within a directory named 'api', skip it
    if [[ $dir == *"/api"* ]]; then
        continue
    fi

    # If the file isn't '_meta.json' or '_app.mdx', delete it
    if [[ "$(basename "$file")" != "_meta.json" ]] && [[ "$(basename "$file")" != "_app.mdx" ]] && [[ "$(basename "$file")" != "pages.md" ]]; then
        rm "$file"
    fi
done

# # Copy the markdown files to the docs folder
cp -R $BUILDDIR/markdown/* "$DOCSDIR"

# Rename example/example.md to example/index.md. This is necessary because the
# markdown files are nested in a folder with the same name as the file and for
# Nextra they should be at the same level
# Use 'find' to search for all directories from the current directory, excluding the current directory
find "$DOCSDIR" -mindepth 1 -type d | while read dir; do
  # If the directory contains a file named "index.md"
  if [[ -f "$dir/index.md" ]]; then
    # Get parent directory path and name
    parent_dir=$(dirname "$dir")
    parent_name=$(basename "$dir")

    # Destination file path
    dest="${parent_dir}/$parent_name.md"

    # Move the file
    mv "$dir/index.md" "$dest"

    # Process the moved file line by line
    while IFS= read -r line; do
      # Ignore lines containing "http" or "mailto"
      if [[ "$line" != *"http"* && "$line" != *"mailto"* ]]; then
        # If the line contains "](", append the parent folder name after it
        echo "${line//](/](/$parent_dir/$parent_name/}" | node rename_link
      else
        echo "$line"
      fi
    done < "$dest" > temp && mv temp "$dest"
  fi
done


# Use find to locate all .md files
find $DOCSDIR -type f -name "*.md" -print0 | while IFS= read -r -d '' file
do
    # Use sed to replace "api/steamship" with "api-reference/steamship"
    sed -i '.bak' 's|api/steamship|api-reference/steamship|g' "$file"
done

# remove all files that end with .bak
find $DOCSDIR -type f -name "*.bak" -delete

# Delete all empty folders
find "$DOCSDIR" -type d -empty -delete

# Remove the _sphinx_design_static folder
rm -rf "$DOCSDIR"/_sphinx_design_static/

# Replace all relative image paths with absolute paths
find "$DOCSDIR" -name '*.md' -exec sed -i '' 's/(\([^)]*.png\))/(\/\1)/g' {} \;

# Remove the /index.md from all links
find "$DOCSDIR" -name "*.md" -exec sed -i '' 's|/index.md||g' {} \;
