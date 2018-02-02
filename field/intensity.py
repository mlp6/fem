class Intensity:
    def __init__(self, dynamat, nodefile='nodes.dyn'):
        self.dynamat = dynamat
        self.nodefile = nodefile
        self.load_intensity()
        self.load_sorted_nodes()

    def load_intensity(self):
        from scipy.io import loadmat

        self.field_intensities = loadmat(self.dynamat)

    def load_sorted_nodes(self):
        from fem.mesh import fem_mesh

        nic = fem_mesh.load_nodeIDs_coords(nodefile=self.nodefile)
        [self.snic, self.axes] = fem_mesh.SortNodeIDs(nic)

    def show_image_plane(self, ele_coord=0):
        from fem.mesh import fem_mesh
        import numpy as np
        import matplotlib.pyplot as plt

        # -1 on next to move to 0 start indexing
        planeNodeIDs = fem_mesh.extractPlane(self.snic, self.axes, (0, ele_coord)) - 1

        image_plane_intensity = np.take(self.field_intensities['intensity'], planeNodeIDs)

        plt.imshow(np.flipud(image_plane_intensity.transpose()))
        plt.show()
