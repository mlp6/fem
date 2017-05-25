class ResSim:
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
        plt.title('t = {:.2f} ms'.format(self.t[0, timestep] * 1e3))
        plt.gca().invert_yaxis()
        plt.show()

        return

    def timeplot(self, axial, lat):
        """plot arfidata through time at specified ax and lat position (mm)

        :param axial: axial depth (mm)
        :param lat: lateral position (mm)
        """
        import matplotlib.pyplot as plt
        import numpy as np

        axInd = np.min(np.where(self.axial >= axial)[0])
        latInd = np.min(np.where(self.lat >= lat)[0])
        t = self.t.transpose()*1e3  # convert from s -> ms
        plt.plot(t, self.arfidata[axInd, latInd, :])
        plt.xlabel('Time (ms)')
        plt.ylabel('Displacement (\mum)')
        plt.title('Axial = {:.1f} mm, Lateral = {:.1f} mm'.
                format(self.axial[axInd][0], self.lat[latInd][0]))
        plt.show()
    
        return

    def play(self, timerange):
        """play an animation

        Strongly recommend not stepping though each timesteps; use some skips!

        :param timerange: range generator of time steps to animate
        """
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

        fig = plt.figure()

        plt.hold(True)

        plt.pcolormesh(self.lat, self.axial, self.arfidata[:, :, 0])
        plt.axes().set_aspect('equal')
        plt.gca().invert_yaxis()
        plt.xlabel('Lateral (mm)')
        plt.ylabel('Axial (mm)')

        anim = animation.FuncAnimation(fig, self.animate, frames=timerange,
                                       blit=False)

        plt.show()
        plt.hold(False)

    def animate(self, i):
        import matplotlib.pyplot as plt
        plt.pcolormesh(self.lat, self.axial, self.arfidata[:, :, i])
        plt.title('t = {:.2f} ms'.format(self.t[0, i] * 1e3))
