class PointLoads:
    def __init__(self, loadfile=None, nodefile='nodes.dyn'):
        self.loadfile = loadfile
        self.nodefile = nodefile
        self.loads = None
        self.load_loads()
        self.load_sorted_nodes()

    def load_loads(self):
        """load point loads from loadfile
        """
        import numpy as np

        self.pt_loads = np.loadtxt(self.loadfile,
                                   comments=['$', '*'],
                                   delimiter=',',
                                   dtype={'names': ('NID', 'Direction', 'LCID',
                                                    'Magnitude', 'None'),
                                          'formats': ('i4', 'i4', 'i4',
                                                      'f4', 'i4')})

    def load_sorted_nodes(self):
        """load-n-sort mesh nodes
        """
        from fem.mesh import fem_mesh

        nic = fem_mesh.load_nodeIDs_coords(nodefile=self.nodefile)
        [self.snic, self.axes] = fem_mesh.SortNodeIDs(nic)

    def show_image_plane(self, ele_coord=0):
        """show an image of the loads on a plane

        :param ele_coord=0: elevation position of the plane
        """
        from fem.mesh import fem_mesh
        import numpy as np
        import matplotlib.pyplot as plt

        # -1 on next to move to 0 start indexing
        planeNodeIDs = fem_mesh.extractPlane(self.snic, self.axes,
                                             (0, ele_coord))

        image_plane_loads = np.zeros(planeNodeIDs.shape)
        for m, a in enumerate(planeNodeIDs):
            for n, nid in enumerate(a):
                b = np.where(self.pt_loads['NID'] == nid)
                #TODO: Handle the direction of the push
                try:
                    image_plane_loads[m][n] = self.pt_loads['Magnitude'][b[0]]
                except:
                    pass

        plt.imshow(np.flipud(image_plane_loads.transpose()))
        plt.show()

    def plot3Dquiver(self):
        """generate 3D quiver plot of all loads
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import axes3d
        import numpy as np

        fig = plt.figure()
        ax = fig.gca(projection='3d')

        dx = np.mean(np.diff(axes[0]))
        dy = np.mean(np.diff(axes[1]))
        dz = np.mean(np.diff(axes[2]))
        X, Y, Z = np.meshgrid(np.arange(self.axes[0][0], self.axes[0][-1], dx),
                              np.arange(self.axes[1][0], self.axes[1][-1], dy),
                              np.arange(self.axes[2][0], self.axes[2][-1], dz))

        #TODO: map load vectors to meshgrid locations

        # https://matplotlib.org/mpl_toolkits/mplot3d/tutorial.html#quiver
        ax.quiver(X, Y, Z, U, V, W, length=0.1, normalize=True)

