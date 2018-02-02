class PointLoads:
    def __init__(self, loadfile, nodefile='nodes.dyn'):
        self.loadfile = loadfile
        self.nodefile = nodefile
        self.loads = None
        self.load_loads()
        self.load_sorted_nodes()

    def load_loads(self):
        import numpy as np

        self.point_loads = np.loadtxt('PointLoads-f1.80-F1.0-FD0.120-a0.50.dyn', comments=['$', '*'],
                                 delimiter=',', dtype={'names': ('NID', 'Direction', 'LCID',
                                                                 'Magnitude', 'None'),
                                                       'formats': ('i4', 'i4', 'i4', 'f4', 'i4')})

    def load_sorted_nodes(self):
        from fem.mesh import fem_mesh

        nic = fem_mesh.load_nodeIDs_coords(nodefile=self.nodefile)
        [self.snic, self.axes] = fem_mesh.SortNodeIDs(nic)

    def show_image_plane(self, ele_coord=0):
        from fem.mesh import fem_mesh
        import numpy as np
        import matplotlib.pyplot as plt

        # -1 on next to move to 0 start indexing
        planeNodeIDs = fem_mesh.extractPlane(self.snic, self.axes,
                                             (0, ele_coord))

        image_plane_loads = np.zeros(planeNodeIDs.shape)
        for m, a in enumerate(planeNodeIDs):
            for n, nid in enumerate(a):
                b = np.where(self.point_loads['NID'] == nid)
                try:
                    image_plane_loads[m][n] = self.point_loads['Magnitude'][b[0]]
                except:
                    pass

        plt.imshow(np.flipud(image_plane_loads.transpose()))
        plt.show()
