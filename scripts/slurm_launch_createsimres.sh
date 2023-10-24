#!/bin/bash
#SBATCH --mail-type=BEGIN,FAIL,END
#SBATCH --mail-user=joeyr@email.unc.edu
#SBATCH --nodes=2
#SBATCH --ntasks=88
#SBATCH --partition=debug_queue
#SBATCH --output=/proj/gallippilab/users/joeyr/dyna_simulations/logs/hourglassing_test/%A-%a_slurmOUT_dyna.out
#SBATCH --error=/proj/gallippilab/users/joeyr/dyna_simulations/logs/hourglassing_test/%A-%a_slurmERR_dyna.out
#SBATCH --job-name=createressim
#SBATCH --time=04:00:00

# Get simulation folder
folder="/proj/gallippilab/users/joeyr/dyna_simulations/hourglassing_test/mesh_size=[51,51,101]/txer=vf73,fd=[0,0,15],fnum=1.5,att=0.5/e=10,v=0.01"

# FEM directory
fem_folder="$HOME/repos/fem"

# createressim directory
res_folder="$HOME/repos/fem_tools"

start_time=$(date +%s)
keyname="Master.dyn"

cd "$folder"

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