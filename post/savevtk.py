""" savevtk.py

methods to save 3D scalar and vector data in ASCII VTK format

Mark Palmeri
mlp6@duke.edu
2016-04-24
"""

class SaveVTK:

    def __init__(self, data, origin, spacing):
        """ initialize the object

        :param float data: [scalar] 3D numpy array
                           [vector] tuple of 3D numpy arrays (X, Y, Z)
        :param float origin: mesh origin tuple (x, y, z)
        :param float spacing: node spacing tuple (x, y, z)
        """
        self.data = data
        self.origin = origin
        self.spacing = spacing

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):
        import numpy as np

        if isinstance(data, np.ndarray):
            self.__data = data
        elif isinstance(data, tuple):

            if ((data[0].shape != data[1].shape) | (data[0].shape != data[2].shape)):
                raise IndexError('The shape of the ndarrays must be the same.')

            self.__data = {}
            self.__data['x'] = data[0]
            self.__data['y'] = data[1]
            self.__data['z'] = data[2]


    def save_scalar(self, filename, dataname="scalars", header_comment=None):
        """save 3D scalar data in VTK structure points format

        :param string filename: output filename
        :param string dataname: data name
        :param string header_comment: default = None
        """
        import numpy as np

        with open(filename, 'w') as vtkfile:
            vtkfile.write("# vtk DataFile Version 2.0\n")
            if header_comment:
                vtkfile.write("%s\n" % (header_comment))
            vtkfile.write("ASCII\n\n")
            vtkfile.write("DATASET STRUCTURED_POINTS\n")
            vtkfile.write("DIMENSIONS    {:d}   {:d}   {:d}\n\n".format(*self.data.shape))
            vtkfile.write("ORIGIN    {:.2f}   {:.2f}   {:.2f}\n".format(*self.origin))
            vtkfile.write("SPACING    {:.3f}   {:.3f}   {:.3f}\n\n".format(*self.spacing))
            vtkfile.write("POINT_DATA   {:d}\n".format(np.prod(self.data.shape)))
            vtkfile.write("SCALARS {} float\n".format(dataname))
            vtkfile.write("LOOKUP_TABLE default\n\n")
            for x in range(0, self.data.shape[0]):
                for y in range(0, self.data.shape[1]):
                    for z in range(0, self.data.shape[2]):
                        vtkfile.write("{:.6e} ".format(self.data[x, y, z]))
                    vtkfile.write(" \n")


    def save_vector(self, filename, dataname="vectors", header_comment=None):
        """save 3D vector array in VTK structure points format

        :param string filename: output filname
        :param string dataname: data name
        :param string header_comment: default = None
        """
        import numpy as np

        with open(filename, 'w') as vtkfile:
            vtkfile.write('# vtk DataFile Version 2.0\n')
            if header_comment:
                vtkfile.write("%s\n" % (header_comment))
            vtkfile.write('ASCII\n')
            vtkfile.write('\n')
            vtkfile.write('DATASET STRUCTURED_POINTS\n')
            vtkfile.write('DIMENSIONS    {:d}   {:d}   {:d}\n'.format(data['x'].shape))
            vtkfile.write('\n');
            vtkfile.write("ORIGIN    {:.2f}   {:.2f}   {:.2f}\n".format(*self.origin))
            vtkfile.write("SPACING   {:.3f}   {:.3f}   {:.3f}\n\n".format(*self.spacing))
            vtkfile.write('\n')
            vtkfile.write('POINT_DATA   {:d}\n'.format(np.prod(dims)))
            vtkfile.write('VECTORS {} float\n'.format(dataname))
            vtkfile.write('\n')
            for a in range(0, self.data['x'].shape[0]):
                for b in range(0, self.data['x'].shape[1]):
                    for c in range(0, self.data['x'].shape[2]):
                        vtkfile.write('%f ', self.data['x'][a, b, c])
                        vtkfile.write('%f ', self.data['y'][a, b, c])
                        vtkfile.write('%f ', self.data['z'][a, b, c])
                    vtkfile.write('\n')
