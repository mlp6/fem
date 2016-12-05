class Res:
    """plot and animate res_sim.mat simulation data
    """
    def __init__(self, filename="res_sim.mat"):
        self.load(filename)


    def load(self, filename):
        """load MATv5 data

        :param filename:
        :returns: attributes - lat, axial, t, arfidata
        """
        from scipy.io import loadmat

        d = loadmat(filename)
        
        self.lat = d['lat']
        self.axial = d['axial'].transpose()
        self.t = d['t']
        self.arfidata = d['arfidata']


    def plot(self, timestep):
        """plot arfidata at specified timestep

        :param timestep: int
        """
        import matplotlib.pyplot as plt

        plt.pcolormesh(self.lat, self.axial, self.arfidata[:, :, timestep])
        plt.axes().set_aspect('equal')
        plt.xlabel('Lateral (mm)')
        plt.ylabel('Axial (mm)')
        plt.title('t = {:.2f} ms'.format(self.t[0, timestep]*1e3))
        plt.gca().invert_yaxis()
        plt.show()

        return
