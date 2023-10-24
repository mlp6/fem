#!/bin/bash

# Read folders from arguments
folder_arr=("$@")

# Get simulation folder
folder="${folder_arr[$SLURM_ARRAY_TASK_ID]}"

# FEM directory
fem_folder="$HOME/repos/fem"

# createressim directory
res_folder="$HOME/repos/fem_tools"

start_time=$(date +%s)
keyname="Master.dyn"

cd "$folder"

echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nSimulating ARF emission for $folder"
echo -e "\n--job $SLURM_ARRAY_JOB_ID\n--array $SLURM_ARRAY_TASK_ID"
echo -e "\nCurrent working directory: $PWD"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n"
$MPI_HOME/bin/mpirun -np $SLURM_NPROCS lsdyna_mpp_d i="${keyname}" memory=20000m memory2=500m

echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nStarting l2a"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
l2a_s binout*   # _d or _s? _s originially but this means single precision?
echo -e "\nFEM displacement simulation has been completed!"

python_start_time=$(date +%s)
python $fem_folder/fem/post/create_disp_dat.py
echo -e "Python create_disp_dat runtime: $(($(date +%s) - $python_start_time))"

matlab_start_time=$(date +%s)
matlabRunStr="addpath(genpath('${res_folder}'));createsimres('nodout','${keyname}','../../nodes.dyn')"
matlab -singleCompThread -batch $matlabRunStr
echo -e "Matlab createsimres runtime: $(($(date +%s) - $matlab_start_time))"

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
# find . -name "nodout" -type f -delete

echo -e "Total execution time: $(($(date +%s) - $start_time))"