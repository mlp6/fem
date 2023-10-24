#!/bin/bash

# Set the name of the job and specify the output file
#SBATCH --job-name=my_python_job
#SBATCH --output=my_python_job_output.txt

# Set the partition and number of CPU cores you want to use
#SBATCH --partition=your_partition
#SBATCH --cpus-per-task=4

# Set the path to your virtual environment activate script
VENV_ACTIVATE="~/.conda/envs/fem"

# Set the path to your Python script
SCRIPT_PATH="./subfolder/your_python_script.py"

# Activate the virtual environment
source activate $VENV_ACTIVATE

# Run the Python script
python $SCRIPT_PATH

# Deactivate the virtual environment
source deactivate
