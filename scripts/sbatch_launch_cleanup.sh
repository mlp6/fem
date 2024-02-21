#!/bin/bash

# Read folders from arguments
folder_arr=("$@")

# Get simulation folder
folder="${folder_arr[$SLURM_ARRAY_TASK_ID]}"

# FEM directory
fem_folder="$HOME/repos/fem"

start_time=$(date +%s)

cd "$folder"

echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nSimulating ARF emission for $folder"
echo -e "\nCurrent working directory: $PWD"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n"

echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nGenerate binary nodout file from binout* FEM files"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
l2a_start_time=$(date +%s)

l2a_s binout*   # could potentially use l2a_d for double precision if necessary in the future

echo -e "Runtime [l2a_s]: $(($(date +%s) - $l2a_start_time))"

echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nCreating disp.dat file"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
create_disp_dat_start_time=$(date +%s)

# C function path
source_file="$fem_folder/fem/post/create_disp_dat_fast.c"

# Executatble path
executable="$fem_folder/fem/post/create_disp_dat_fast"

# Check if the executable exists
if [ -e "$executable" ]; then
    echo "Executable already exists."
else
    # Check if the source file exists
    if [ -e "$source_file" ]; then
        # Compile the source file to create the executable
        gcc -o "$executable" "$source_file"
        echo "Compilation successful."
    else
        echo "Error: Source file '$source_file' not found."
    fi
fi

# Run compiled create_disp_dat_fast
$executable -o ./disp.dat -i ./nodout

echo -e "Runtime [create_disp_dat]: $(($(date +%s) - $create_disp_dat_start_time))"

echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nConvert disp.dat to res_sim.mat"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
create_res_sim_start_time=$(date +%s)

# Run function to convert from disp.dat to res_sim.mat
python $fem_folder/fem/dyna/post.py

echo -e "Runtime [create_res_sim]: $(($(date +%s) - $create_res_sim_start_time))"

echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nClean up simulation files"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
cleanup_files_start_time=$(date +%s)

find . -name "adptmp" -type f -delete
find . -name "bg_switch*" -type f -delete
find . -name "binout*" -type f -delete
find . -name "core*" -type f -delete
find . -name "disk*" -type f -delete
find . -name "d3dump*" -type f -delete
find . -name "d3*" -type f -delete
find . -name "glstat" -type f -delete
find . -name "kill_by_pid" -type f -delete
find . -name "load_profile*" -type f -delete
find . -name "*lsda*" -type f -delete
find . -name "mes0*" -type f -delete
find . -name "mpptbin*" -type f -delete
find . -name "part_des*" -type f -delete
find . -name "rf0*" -type f -delete
find . -name "scr*" -type f -delete
find . -name "spool*" -type f -delete
find . -name "status.out" -type f -delete
find . -name "nodout" -type f -delete
echo -e "Runtime [cleanup_files]: $(($(date +%s) - $cleanup_files_start_time))"

echo -e "Runtime [total]: $(($(date +%s) - $start_time))"

sleep 5m