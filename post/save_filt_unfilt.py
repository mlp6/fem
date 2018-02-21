""" save_filt_unfilt.py
"""

def main():
    from h5py import File
    from savevtk import SaveVTK

    data = File("Filt4D_R1_Seed0.mat")

    unfilt = get_proc_data(data, "sws4D_unfilt")
    filt = get_proc_data(data, "sws4D_4Dfilt")

    unfiltvtk = SaveVTK(unfilt, (11.5, -1.5, -9.5), (0.1, 0.1, 0.1))
    filtvtk = SaveVTK(filt, (11.5, -1.5, -9.5), (0.1, 0.1, 0.1))

    unfiltvtk.save_scalar("unfilt.vtk", data_name="SWS",
                          header_comment="Unfiltered 4D Data")
    filtvtk.save_scalar("filt4d.vtk", data_name="SWS",
                        header_comment="Filtered 4D Data")


def get_proc_data(data, keyname, data_ceiling=2.5):
    """ extract data from dict and process it

    :param data: HDF5 data dict
    :param keyname: keyname to get
    :param data_ceiling: max value to clip data (default = 2.5)
    :returns: filt_data (np.array)
    """

    import numpy as np
    from scipy.signal import medfilt

    filt_data = np.array(data[keyname], order="F")
    filt_data = np.abs(filt_data)
    filt_data.clip(0, data_ceiling, filt_data)
    filt_data = medfilt(filt_data, [5, 5, 5])

    return filt_data


if __name__ == "__main__":
    main()
