#!/bin/bash
# Step 1: Read base path argument into the variable BASE_PATH
BASE_PATH="$1"

# Step 2: Find all subfolders that have a file "ultratrack_params.m"
ALL_ULTRATRACK_SIM_FOLDERS=($(find "$BASE_PATH" -type f -name "ultratrack_params.mat" -exec dirname {} \;))

# Step 3: Loop over ALL_ULTRATRACK_SIM_FOLDERS and find incomplete folders
# Sim is complete if it has at least one file that matches the pattern "all_rf_lines*.mat" and at least one file that matches the pattern "res_tracksim*.mat"
INCOMPLETE_ULTRATRACK_SIM_FOLDERS=()
for folder in "${ALL_ULTRATRACK_SIM_FOLDERS[@]}"; do
    # Check if folder does not have files matching the specified patterns
    if ! ls "$folder"/all_rf_lines*.mat >/dev/null 2>&1 || ! ls "$folder"/res_tracksim*.mat >/dev/null 2>&1; then
        INCOMPLETE_ULTRATRACK_SIM_FOLDERS+=("$folder")
    fi
done

# Print the incomplete folders found
for folder in "${INCOMPLETE_ULTRATRACK_SIM_FOLDERS[@]}"; do
    echo "$folder"
done
