import os
import sys
import glob


def write_folders_to_file(folder_list, file_path):
    with open(file_path, "w") as file:
        for folder in folder_list:
            file.write(folder + "\n")


def find_incomplete_dyna_sim_folders(base_path):
    folders = []
    for dirpath, dirnames, filenames in os.walk(base_path):
        if "Master.dyn" in filenames and "res_sim.mat" not in filenames:
            folders.append(dirpath)
    return folders


def find_disp_dat_folders(base_path):
    folders = []
    for dirpath, dirnames, filenames in os.walk(base_path):
        if "disp.dat" in filenames:
            folders.append(dirpath)
    return folders


def find_incomplete_ultratrack_sim_folders(base_path):
    folders = []
    for dirpath, dirnames, filenames in os.walk(base_path):
        if "ultratrack_params.mat" in filenames:
            rf_lines_files = glob.glob(dirpath + "/" + "all_rf_lines*.mat")
            res_tracksim_files = glob.glob(dirpath + "/" + "res_tracksim*.mat")
            if len(rf_lines_files) and len(res_tracksim_files):
                folders.append(dirpath)
    return folders


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
