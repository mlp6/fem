#!/bin/bash

# Read folders from arguments
folder_arr=("$@")

# Get simulation folder
folder="${folder_arr[$SLURM_ARRAY_TASK_ID]}"

start_time=$(date +%s)
keyname="Master.dyn"

cd "$folder"

echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nSimulating ARF emission for $folder"
echo -e "\n--job $SLURM_ARRAY_JOB_ID\n--array $SLURM_ARRAY_TASK_ID"
echo -e "\nCurrent working directory: $PWD"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n"
$MPI_HOME/bin/mpirun -np $SLURM_NPROCS lsdyna_mpp_d i="${keyname}" memory=20000m memory2=500m

echo -e "Runtime [lsdyna_mpp_d]: $(($(date +%s) - $start_time))"