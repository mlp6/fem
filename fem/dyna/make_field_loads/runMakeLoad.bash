#!/bin/bash
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --mail-user=joeyr@email.unc.edu
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -p general
#SBATCH --mem-per-cpu=10g
#SBATCH --output=/proj/gallippilab/users/joeyr/batch_load_simulations/logs/%A-%a_slurmOUT_load_sims.out
#SBATCH --error=/proj/gallippilab/users/joeyr/batch_load_simulations/logs/%A-%a_slurmERR_load_sims.out
#SBATCH --time=03:00:00
#SBATCH --array=[1-1395]

module load matlab/2021a
matlab -batch "makeLoad(${SLURM_ARRAY_TASK_ID})"