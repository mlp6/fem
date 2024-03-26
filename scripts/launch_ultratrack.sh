#!/bin/bash

config_folder=phantom_match/
ultratrack_base_folder=$config_folder
run_ultratrack_config=0
run_ultratrack_sbatch=0


# find all folders with disp.dat
echo -e "Searching for disp.dat files under $ultratrack_base_folder"
disp_dat_folders=($(find_folders_with_dispdat.sh $ultratrack_base_folder))
n_disp_dat_folders=${#disp_dat_folders[@]}
echo -e "Found $n_disp_dat_folders folders with disp.dat files under $ultratrack_base_folder"

# save to file
printf "%s\n" "${disp_dat_folders[@]}" > disp_folders.txt

# run ultratrack config
    # sets up folders for every parameter combination under each disp.dat folder
    # saves file with all ultratrack parameter structures
if [ $run_ultratrack_config == 1 ]; then
    echo -e "Setting up ultratrack folders..."
    matlab -batch "addpath('${config_folder}'); ultratrack_config()"
fi

# find all subfolders under disp.dat that dont have all_rf_lines and res_tracksim files
echo -e "Searching for incomplete ultratrack simulation folders under $ultratrack_base_folder"
inc_sim_folders=($(find_incomplete_ultratrack_sims.sh $ultratrack_base_folder))
n_inc_sim_folders=${#inc_sim_folders[@]}
echo -e "Found $n_inc_sim_folders incomplete ultratrack simulation folders under $ultratrack_base_folder"

# save to file
printf "%s\n" "${inc_sim_folders[@]}" > incomplete_ultratrack_sim_folders.txt

if [ $run_ultratrack_sbatch == 1 ]; then
    # launch job array over all incomplete subfolders
    # Setup slurm logs folder (if it doesn't exist)
    log_folder="${PWD}/logs/ultratrack/$ultratrack_base_folder"
    mkdir -p $log_folder

    NAME="ultra"
    TIME="16:00:00"
    sbatch -p general -N 1 -n 1 --mem=4g --cpus-per-task=8 -t $TIME --job-name=$NAME --output=$log_folder/%A-%a-out.log --error=$log_folder/%A-%a-err.log --mail-type=BEGIN,FAIL,END --mail-user=$USER@email.unc.edu --array=[1-$n_inc_sim_folders] --wrap "matlab -batch \"addpath(genpath(fullfile(getenv('HOME'), 'repos', 'ultratrack'))); ultratrack();\""
fi
