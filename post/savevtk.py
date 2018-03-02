""" savevtk.py

methods to save 3D scalar and vector data in ASCII VTK format

Mark Palmeri
mlp6@duke.edu
2016-04-24
"""

class SaveVTK:

    def __init__(self, data, origin, spacing):
        """ initialize the object

        :param data: 3D data
        :param origin: (x, y, z)
        :param spacing: (x, y, z)
        """
        self.data = data
        self.origin = origin
        self.spacing = spacing


    def save_scalar(self, filename, data_name="scalars", header_comment=None):
        """save 3D scalar data in VTK structure points format

        :param filename:
        :param data_name:
        :param header_comment: default = None
        """
        import numpy as np

        with open(filename, 'w') as vtkfile:
            vtkfile.write("# vtk DataFile Version 2.0\n")
            if header_comment:
                vtkfile.write("%s\n" % (header_comment))
            vtkfile.write("ASCII\n\n")
            vtkfile.write("DATASET STRUCTURED_POINTS\n")
            vtkfile.write("DIMENSIONS    %d   %d   %d\n\n" % (self.data.shape))
            vtkfile.write("ORIGIN    %.2f   %.2f   %.2f\n" % (self.origin))
            vtkfile.write("SPACING    %.3f   %.3f   %.3f\n\n" % (self.spacing))
            vtkfile.write("POINT_DATA   %d\n" % (np.prod(self.data.shape)))
            vtkfile.write("SCALARS %s float\n" % data_name)
            vtkfile.write("LOOKUP_TABLE default\n\n")
            for x in range(0, self.data.shape[0]):
                for y in range(0, self.data.shape[1]):
                    for z in range(0, self.data.shape[2]):
                        vtkfile.write("%.6e " % self.data[x, y, z])
                    vtkfile.write(" \n")

        return 0
