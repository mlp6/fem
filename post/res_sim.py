class ResSim:
    """plot and animate res_sim.mat simulation data
    """
    def __init__(self):
        pass


    def __str__():
        pass

    def load(self, filename='res_sim.mat'):
        """load MATv5 data

        Creates 'res' dict containing:
        * lat
        * axial
        * t
        * arfidata (3D)

        :param filename:
        """
        from scipy.io import loadmat

        self.res = loadmat(filename)
        print(self.res.keys())

        return


    def plot(self, timestep):
        """plot arfidata at specified timestep

        :param timestep: int
        """
        import matplotlib.pyplot as plt

        plt.pcolormesh(self.res['lat'], self.res['axial'].transpose(), self.res['arfidata'][:, :, timestep])
        plt.axes().set_aspect('equal')
        plt.xlabel('Lateral (mm)')
        plt.ylabel('Axial (mm)')
        plt.title('t = {:.2f} ms'.format(self.res['t'][0, timestep]*1e3))
        plt.gca().invert_yaxis()
        plt.show()

        return