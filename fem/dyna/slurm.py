import subprocess
from simple_slurm import Slurm
import os
import pathlib

CPUS_PER_NODE = 44
ONYEN = os.environ["USER"]
DYNA_DEBUG_RESOURCES = dict(
    partition="debug_queue",
    nodes=1,
    ntasks=CPUS_PER_NODE * 1,  # cpus per node * number of nodes
    time="00:02:00",
    job_name="dyna",
    mail_type="FAIL",
    mail_user=f"{ONYEN}@email.unc.edu",
)
DYNA_2112_RESOURCES = dict(
    partition="2112_queue",
    nodes=13,
    ntasks=CPUS_PER_NODE * 13,  # cpus per node * number of nodes
    time="3:00:00",
    job_name="dyna",
    mail_type="FAIL",
    mail_user=f"{ONYEN}@email.unc.edu",
)
DYNA_528_RESOURCES = dict(
    partition="528_queue",
    nodes=4,
    ntasks=CPUS_PER_NODE * 4,  # cpus per node * number of nodes
    time="6:00:00",
    job_name="dyna",
    mail_type="FAIL",
    mail_user=f"{ONYEN}@email.unc.edu",
)
# DYNA_528_RESOURCES = dict(
#     partition="528_queue",
#     nodes=12,
#     ntasks=CPUS_PER_NODE * 12,  # cpus per node * number of nodes
#     time="3:30:00",
#     job_name="dyna",
#     mail_type="FAIL",
#     mail_user=f"{ONYEN}@email.unc.edu",
# )
CLEANUP_RESOURCES = dict(
    partition="cleanup_queue",
    nodes=1,
    ntasks=1,
    time="6:00:00",
    job_name="cleanup",
    mem="75G",
    mail_type="FAIL",
    mail_user=f"{ONYEN}@email.unc.edu",
)
ULTRATRACK_RESOURCES = dict(
    partition="general",
    nodes=1,
    ntasks=1,
    time="16:00:00",
    job_name="ultratrack",
    mem="4G",
    cpus_per_task=8,
    mail_type="FAIL",
    mail_user=f"{ONYEN}@email.unc.edu",
)


CLEANUP_SIMULATION_FILES_LINES = r"""
# Cleanup files from any previous attempts to run simulation
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nClean up temporary simulation files"
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
find . -name "nodout" -type f -delete
find . -name "status.out" -type f -delete
find . -name "CLEANUP_READY.txt" -type f -delete
echo -e "Runtime [cleanup_files]: $(($(date +%s) - $cleanup_files_start_time))"
"""

PWD_LINES = r"""
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nCurrent working directory: $PWD"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n"
"""

DYNA_SIMULATION_LINES = r"""
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nSimulating ARF emissions applied to FEM mesh"
echo -e "\n--partition $SLURM_JOB_PARTITION"
echo -e "\n--job $SLURM_JOB_ID"
echo -e "\n--job_array $SLURM_ARRAY_JOB_ID"
echo -e "\n--job_array_task_id $SLURM_ARRAY_TASK_ID"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n"
$MPI_HOME/bin/mpirun -np $SLURM_NPROCS lsdyna_mpp_d i="Master.dyn" memory=20000m memory2=500m
"""

L2A_LINES = r"""
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nGenerate binary nodout file from binout* FEM files"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
l2a_start_time=$(date +%s)

l2a_s binout*   # could potentially use l2a_d for double precision if necessary in the future

echo -e "Runtime [l2a_s]: $(($(date +%s) - $l2a_start_time))"
"""

CREATE_DISP_DAT_LINES = r"""
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
"""

CREATE_RES_SIM_LINES = r"""
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
echo -e "\nConvert disp.dat to res_sim.mat"
echo -e "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
create_res_sim_start_time=$(date +%s)

# Run function to convert from disp.dat to res_sim.mat
python $fem_folder/fem/dyna/post.py

echo -e "Runtime [create_res_sim]: $(($(date +%s) - $create_res_sim_start_time))"
"""


def get_job_ids(user, partition, job_state="PD,R"):
    try:
        # Command to get the user's queued jobs in the specified partition
        cmd = [
            "squeue",
            "-u",
            user,
            "-p",
            partition,
            "-r",  # different line for each job in array
            "-h",
            "-t",
            job_state,
            "-o",
            "%i",
        ]

        # Run the command and capture the output
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Check if there's an error
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None

        # Process the output to get an array of job ids
        job_ids = result.stdout.strip().splitlines()
        return job_ids

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def setup_dyna_simulation_folders(log_folder, n_sim_folders, sim_setup_script_name):
    log_folder.mkdir(parents=True, exist_ok=True)

    ONYEN = os.environ["USER"]
    slurm = Slurm(
        output=f"{log_folder}/%A-%a-out.log",
        error=f"{log_folder}/%A-%a-err.log",
        partition="general",
        nodes=1,
        ntasks=1,
        time="01:00:00",
        job_name="sim_setup",
        mail_type="FAIL",
        mail_user=f"{ONYEN}@email.unc.edu",
        array=range(0, n_sim_folders),
    )
    slurm.add_cmd("source activate fem")
    slurm.add_cmd(f"python {sim_setup_script_name}")
    return slurm


def setup_ultratrack_simulation_folders(
    log_folder, ultratrack_setup_script_full_path, sim_folder_filename
):
    log_folder.mkdir(parents=True, exist_ok=True)
    ultratrack_setup_script_full_path = pathlib.Path(ultratrack_setup_script_full_path)
    config_folder = ultratrack_setup_script_full_path.parents[0]
    ultratrack_setup_script_name = ultratrack_setup_script_full_path.stem

    ONYEN = os.environ["USER"]
    slurm = Slurm(
        output=f"{log_folder}/%A-%a-out.log",
        error=f"{log_folder}/%A-%a-err.log",
        partition="general",
        nodes=1,
        ntasks=1,
        time="01:00:00",
        job_name="ultratrack_setup",
        mail_type="FAIL",
        mail_user=f"{ONYEN}@email.unc.edu",
    )
    slurm.add_cmd(f"config_folder={config_folder}")
    slurm.add_cmd(f"sim_folder_filename={sim_folder_filename}")
    slurm.add_cmd(
        f"""matlab -batch \"addpath('${{config_folder}}'); {ultratrack_setup_script_name}('${{sim_folder_filename}}')\""""
    )
    return slurm


def setup_dyna_job(log_folder, sim_folder, resources):
    log_folder.mkdir(parents=True, exist_ok=True)

    slurm = Slurm(
        **resources,
        output=f"{log_folder}/%A-%a-out.log",
        error=f"{log_folder}/%A-%a-err.log",
    )
    slurm.add_cmd("start_time=$(date +%s)")
    slurm.add_cmd(f'folder="{sim_folder}"')
    slurm.add_cmd('cd "$folder"')
    slurm.add_cmd(PWD_LINES)
    slurm.add_cmd(CLEANUP_SIMULATION_FILES_LINES)
    slurm.add_cmd(DYNA_SIMULATION_LINES)
    slurm.add_cmd('echo -e "Runtime [lsdyna_mpp_d]: $(($(date +%s) - $start_time))"')
    slurm.add_cmd("touch CLEANUP_READY.txt")
    return slurm


def setup_cleanup_job(log_folder, sim_folder, resources):
    log_folder.mkdir(parents=True, exist_ok=True)

    slurm = Slurm(
        **resources,
        output=f"{log_folder}/%A-%a-out.log",
        error=f"{log_folder}/%A-%a-err.log",
    )
    slurm.add_cmd("start_time=$(date +%s)")
    slurm.add_cmd(f'folder="{sim_folder}"')
    slurm.add_cmd('cd "$folder"')
    slurm.add_cmd('fem_folder="$HOME/repos/fem"')
    slurm.add_cmd(PWD_LINES)
    slurm.add_cmd(L2A_LINES)
    slurm.add_cmd(CREATE_DISP_DAT_LINES)
    slurm.add_cmd(CREATE_RES_SIM_LINES)
    slurm.add_cmd(CLEANUP_SIMULATION_FILES_LINES)
    slurm.add_cmd('echo -e "Runtime [total]: $(($(date +%s) - $start_time))"')
    slurm.add_cmd("sleep 5m")  # make sure cleanup is done before exiting job
    return slurm


def setup_ultratrack_job(log_folder, sim_folder, ultratrack_script_name, resources):
    log_folder.mkdir(parents=True, exist_ok=True)

    slurm = Slurm(
        **resources,
        output=f"{log_folder}/%A-%a-out.log",
        error=f"{log_folder}/%A-%a-err.log",
    )
    slurm.add_cmd(f'sim_folder="{sim_folder}"')
    slurm.add_cmd(
        f"""matlab -batch \"addpath(genpath(fullfile(getenv('HOME'), 'repos', 'ultratrack'))); {ultratrack_script_name}('${{sim_folder}}')\""""
    )
    return slurm
