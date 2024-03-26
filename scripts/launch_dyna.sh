#!/bin/bash

# run on dogwood with: sh launch_dyna.sh ./folder_to_setup_simulations.py

sim_folder=$1

# Slurm sbatch arguments
PARTITION="2112_queue"
# PARTITION="528_queue"
# NODES=4
# TASKS=176
NODES=13
TASKS=572
NAME="dyna"
TIME="05:00:00"

# Setup slurm logs folder (if it doesn't exist)
log_folder="${PWD}/logs/$sim_folder/phase=${NAME}"
mkdir -p $log_folder

# Find folders to dyna sims
# chmod 777 find_incomplete_dyna_sims.sh
folders=($(find_incomplete_dyna_sims.sh $sim_folder))
n_folders=${#folders[@]}
echo -e "Found $n_folders folders with incomplete simulations under $sim_folder"

# Count folders for job array allocation (N-1 for 0 based indexing)
# Prevent launching more jobs than is permitted for each partition
if [[ $PARTITION == '2112_queue' && $n_folders -gt 20 ]]; then
    # Condition 1: PARTITION is '2112_queue' and n_folders is greater than 20
    job_array_max=19
    echo -e "Lauching on $PARTITION partition with the first 20 jobs"
elif [[ $PARTITION == '528_queue' && $n_folders -gt 30 ]]; then
    # Condition 2: PARTITION is '528_queue' and n_folders is greater than 30
    job_array_max=29
    echo -e "Lauching on $PARTITION partition with the first 30 jobs"
else
    job_array_max=$(( $n_folders - 1 ))
    echo -e "Lauching on $PARTITION partition $n_folders jobs"
fi

# Submit job array
job_id=$(sbatch --parsable -p $PARTITION -N $NODES -n $TASKS -t $TIME --job-name=$NAME --output=$log_folder/%A-%a-out.log --error=$log_folder/%A-%a-err.log --mail-type=BEGIN,FAIL,END --mail-user=$USER@email.unc.edu --array=[0-$job_array_max] sbatch_launch_dyna.sh "${folders[@]}")

# Slurm sbatch arguments
PARTITION="cleanup_queue"
NODES=1
TASKS=1
NAME="cleanup"
# TIME="4:00:00"
TIME="03:00:00"

# Setup slurm logs folder (if it doesn't exist)
log_folder="${PWD}/logs/$sim_folder/phase=${NAME}"
mkdir -p $log_folder

sbatch --dependency=aftercorr:$job_id --mem=20G -p $PARTITION -N $NODES -n $TASKS -t $TIME --job-name=$NAME --output=$log_folder/%A-%a-out.log --error=$log_folder/%A-%a-err.log --mail-type=BEGIN,FAIL,END --mail-user=$USER@email.unc.edu --array=[0-$job_array_max] sbatch_launch_cleanup.sh "${folders[@]}" 
