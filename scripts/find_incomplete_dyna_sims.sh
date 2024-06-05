#!/bin/bash

# Argument 
BASE_PATH="$1"

echo $BASE_PATH

# Initialize the FOLDERS array
FOLDERS=()

# Search for directories with "Master.dyn" and without "res_sim.mat"
while IFS= read -r -d $'\0' directory; do
  echo $directory
  if [[ ! -e "$directory/res_sim.mat" && -f "$directory/Master.dyn" ]]; then
    FOLDERS+=("$directory")
  fi
done < <(find $BASE_PATH -type d -print0)

# Print the found directories 
for folder in "${FOLDERS[@]}"; do
  echo "$folder"
done
