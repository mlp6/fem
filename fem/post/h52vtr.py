class H52VTR:
    """Convert HDF5 file to rectilinear VTR file.

    Args:
        h5file (str): input HDF5 filename
        axisnames (str): ('elev', 'lat', 'axial')
        dataname (str): 'arfidata'
        vtrname (str): 'rectilinear'
    """

    def __init__(self, h5file=None, axisnames=('elev', 'lat', 'axial'),
                 dataname='arfidata', vtrname='rectilinear'):
        self.h5file = h5file
        self.axisnames = axisnames
        self.dataname = dataname
        self.vtrname = vtrname

        self.read_h5data()
        self.read_h5axes()

    def read_h5data(self):
        """Read data in from HDF5 file."""

        import h5py
        import numpy as np

        d = h5py.File(self.h5file)
        self.data = np.array(d[self.dataname])

    def read_h5axes(self):
        """Read axes from HDF5 file."""
        import h5py
        import numpy as np

        d = h5py.File(self.h5file)
        self.axis0 = np.array(d[self.axisnames[0]]).ravel()
        self.axis1 = np.array(d[self.axisnames[1]]).ravel()
        self.axis2 = np.array(d[self.axisnames[2]]).ravel()

    def write_vtr(self):
        """Write rectilinear VTR file."""
        from pyevtk.hl import gridToVTK

        gridToVTK(self.vtrname, self.axis0, self.axis1, self.axis2,
                  pointData={self.dataname: self.data})
