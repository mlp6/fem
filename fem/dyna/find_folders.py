import os
import sys
import glob
import json
import pathlib


def load_json_file(filepath):
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as e:
        # Handle JSON errors or file read errors
        return []


def write_to_json_file(data, filepath):
    try:
        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)
    except OSError as e:
        print(f"Error saving to file: {e}")


def write_folders_to_file(folder_list, file_path):
    with open(file_path, "w") as file:
        for folder in folder_list:
            file.write(folder + "\n")


def read_folders_from_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        # Strip newline characters from each line
        file_list = [line.strip() for line in lines]
    return file_list


def find_all_sim_folders(base_path):
    folders = []
    for dirpath, dirnames, filenames in os.walk(base_path):
        if "Master.dyn" in filenames:
            folders.append(dirpath)
    return folders


def find_incomplete_dyna_sim_folders(sim_folder_list):
    incomplete_sim_folders = []
    for folder in sim_folder_list:
        filenames = [x.name for x in pathlib.Path(folder).glob("*") if x.is_file()]
        if (
            "Master.dyn" in filenames
            and "CLEANUP_READY.txt" not in filenames
            and ("res_sim.mat" not in filenames or "disp.dat" not in filenames)
        ):
            incomplete_sim_folders.append(folder)
    return incomplete_sim_folders


def find_cleanup_ready_sim_folders(sim_folder_list):
    cleanup_ready_sim_folders = []
    for folder in sim_folder_list:
        filenames = [x.name for x in pathlib.Path(folder).glob("*") if x.is_file()]
        if (
            "Master.dyn" in filenames
            and "CLEANUP_READY.txt" in filenames
            and ("res_sim.mat" not in filenames or "disp.dat" not in filenames)
        ):
            cleanup_ready_sim_folders.append(folder)
    return cleanup_ready_sim_folders


def find_complete_dyna_sim_folders(sim_folder_list):
    complete_sim_folders = []
    for folder in sim_folder_list:
        filenames = [x.name for x in pathlib.Path(folder).glob("*") if x.is_file()]
        if (
            "Master.dyn" in filenames
            and "CLEANUP_READY.txt" not in filenames
            and "res_sim.mat" in filenames
            and "disp.dat" in filenames
        ):
            complete_sim_folders.append(folder)
    return complete_sim_folders


def find_ultratrack_folders(folder_list):
    ultratrack_folders = []
    for folder in folder_list:
        for dirpath, dirnames, filenames in os.walk(folder):
            if "ultratrack_params.mat" in filenames:
                ultratrack_folders.append(dirpath)
    return ultratrack_folders


def find_complete_ultratrack_sim_folders(ultratrack_folder_list):
    complete_ultratrack_folders = []
    for folder in ultratrack_folder_list:
        rf_lines_files = list(pathlib.Path(folder).glob("all_rf_lines*.mat"))
        res_tracksim_files = list(pathlib.Path(folder).glob("res_tracksim*.mat"))

        if len(rf_lines_files) and len(res_tracksim_files):
            complete_ultratrack_folders.append(folder)
    return complete_ultratrack_folders


# def find_disp_dat_folders(base_path):
#     folders = []
#     for dirpath, dirnames, filenames in os.walk(base_path):
#         if "disp.dat" in filenames:
#             folders.append(dirpath)
#     return folders


# def find_incomplete_ultratrack_sim_folders(base_path):
#     folders = []
#     for dirpath, dirnames, filenames in os.walk(base_path):
#         if "ultratrack_params.mat" in filenames:
#             rf_lines_files = glob.glob(dirpath + "/" + "all_rf_lines*.mat")
#             res_tracksim_files = glob.glob(dirpath + "/" + "res_tracksim*.mat")
#             if len(rf_lines_files) and len(res_tracksim_files):
#                 folders.append(dirpath)
#     return folders


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m find_folders option base_path")
        sys.exit(1)

    option = sys.argv[1]
    base_path = sys.argv[2]

    if option == "incomplete_dyna":
        folders = find_incomplete_dyna_sim_folders(base_path)
        filename = "incomplete_dyna_sim_folders.txt"
    elif option == "disp_dat":
        folders = find_disp_dat_folders(base_path)
        filename = "disp_dat_folders.txt"
    elif option == "incomplete_ultratrack":
        folders = find_incomplete_ultratrack_sim_folders(base_path)
        filename = "incomplete_ultratrack_sim_folders.txt"
    else:
        print(
            "Invalid option. Please choose one of: incomplete_dyna, disp_dat, incomplete_ultratrack"
        )

    write_folders_to_file(folders, filename)
