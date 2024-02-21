#!/bin/bash
#SBATCH --nodes=1
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --job-name=sim_setup
#SBATCH --output=./logs/setup/setup_sims.%A-%a.out
#SBATCH --error=./logs/setup/setup_sims.%A-%a.err
#SBATCH --partition=general
#SBATCH --array=[0-3]

# run on longleaf with: sbatch launch_setup_sims.sh ./folder_to_setup_simulations.py

folder=$1

source activate fem
python $folder/setup_simulations.py
