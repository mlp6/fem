#!/bin/bash

# input argument for sim_folder
# Clone fem repo if it doesn't exist in home
# Check modules are added
# Suggested timing table
# - partition
# - number of nodes
# - grid size
# - material properties

sim_folder=./hourglassing_test
# sim_folder=./phantom_matched_cylinder_node_set

# Slurm sbatch arguments
# PARTITION="debug_queue"
PARTITION="2112_queue"
# PARTITION="528_queue"
# NODES=2
# TASKS=88
# NODES=4
# TASKS=176
NODES=13
TASKS=572
NAME="dyna_hour"
TIME="8:00:00"

# Setup slurm logs folder (if it doesn't exist)
log_folder="${PWD}/logs/$sim_folder/${NAME}"
mkdir -p $log_folder

# Find folders to dyna sims
chmod 777 ./find_incomplete_dyna_sims.sh
folders=($(./find_incomplete_dyna_sims.sh $sim_folder))

# Count folders for job array allocation (N-1 for 0 based indexing)
job_array_max=$(( ${#folders[@]} - 1 ))

# Submit job array
sbatch -p $PARTITION -N $NODES -n $TASKS -t $TIME --job-name=$NAME --output=$log_folder/%A-%a-out.log --error=$log_folder/%A-%a-err.log --mail-type=BEGIN,FAIL,END --mail-user=$USER@email.unc.edu --array=[0-$job_array_max] ./slurm_launch_dyna_sims.sh "${folders[@]}"
