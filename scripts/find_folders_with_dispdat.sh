#!/bin/bash

# Argument 
BASE_PATH="$1"

# Initialize the FOLDERS array
FOLDERS=()

# Search for directories with "disp.dat"
while IFS= read -r -d $'\0' directory; do
  if [[ -f "$directory/disp.dat" ]]; then
    FOLDERS+=("$directory")
  fi
done < <(find $BASE_PATH -type d -print0)

# Print the found directories 
for folder in "${FOLDERS[@]}"; do
  echo "$folder"
done
