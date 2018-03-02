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
        import numpy as np

        # TODO: create a data object
        if isinstance(data, np.ndarray):
            self.data = data
        elif isinstance(data, tuple):
            self.data.X = data[0]
            self.data.Y = data[1]
            self.data.Z = data[2]
        self.origin = origin
        self.spacing = spacing


    def save_scalar(self, filename, header_comment=None):
        """save 3D scalar data in VTK structure points format

        :param string filename: output filename
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
            vtkfile.write("SPACING    {:.3f}   {.3f}   {.3f}\n\n".format(*self.spacing))
            vtkfile.write("POINT_DATA   {:d}\n".format(np.prod(self.data.shape)))
            vtkfile.write("SCALARS scalars float\n")
            vtkfile.write("LOOKUP_TABLE default\n\n")
            for x in range(0, self.data.shape[0]):
                for y in range(0, self.data.shape[1]):
                    for z in range(0, self.data.shape[2]):
                        vtkfile.write("%.6e " % self.data[x, y, z])
                    vtkfile.write(" \n")


    def save_vector(self, filename, header_comment=None):
        """save 3D vector array in VTK structure points format

        :param string filename: output filname
        :param string header_comment: default = None
        """
        import numpy as np

        # TODO: move this check when initializing the data object
        if ((size(X) != size(Y)) | (size(X) != size(Z))):
            fprint('Error: velocity arrays of unequal size\n'); return;
        end

        with open(filename, 'w') as vtkfile:
            vtkfile.write('# vtk DataFile Version 2.0\n')
            if header_comment:
                vtkfile.write("%s\n" % (header_comment))
            vtkfile.write('ASCII\n')
            vtkfile.write('\n')
            vtkfile.write('DATASET STRUCTURED_POINTS\n')
            vtkfile.write('DIMENSIONS    {:d}   {:d}   {:d}\n'.format(data.X.shape))
            vtkfile.write('\n');
            vtkfile.write("ORIGIN    {:.2f}   {:.2f}   {:.2f}\n".format(*self.origin))
            vtkfile.write("SPACING   {:.3f}   {:.3f}   {:.3f}\n\n".format(*self.spacing))
            vtkfile.write('\n')
            vtkfile.write('POINT_DATA   {:d}\n'.format(np.prod(dims)))
            vtkfile.write('VECTORS vectors float\n')
            vtkfile.write('\n')
            for a in range(0, self.data.X.shape[0]):
                for b in range(0, self.data.X.shape[1]):
                    for c in range(0, self.data.X.shape[2]):
                        vtkfile.write('%f ', self.data.X[a, b, c])
                        vtkfile.write('%f ', self.data.Y[a, b, c])
                        vtkfile.write('%f ', self.data.Z[a, b, c])
                    vtkfile.write('\n')
