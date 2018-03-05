class ResSim:
    """plot and animate res_sim.mat simulation data"""

    def __init__(self, filename="res_sim.mat"):
        self.load(filename)

    def load(self, filename):
        """load MATv5 data

        Args:
            filename (str): input filename

        Returns:
            attributes (ndarray): [lat, axial, t, arfidata]

        """
        from scipy.io import loadmat

        d = loadmat(filename)

        self.lat = d['lat'].squeeze()
        self.axial = d['axial'].squeeze()
        self.t = d['t'].squeeze() * 1e3  # convert from s -> ms
        self.arfidata = d['arfidata']

    def plot(self, timestep):
        """Plot arfidata at specified timestep.

        Args:
            timestep (int):

        Returns:

        """
        import matplotlib.pyplot as plt

        plt.pcolormesh(self.lat, self.axial, self.arfidata[:, :, timestep])
        plt.axes().set_aspect('equal')
        plt.xlabel('Lateral (mm)')
        plt.ylabel('Axial (mm)')
        plt.title('t = {:.2f} ms'.format(self.t[timestep]))
        plt.gca().invert_yaxis()
        plt.show()

        return

    def timeplot(self, axial, lat):
        """plot arfidata through time at specified ax and lat position (mm)

        Args:
            axial (ndarray): axial depth (mm)
            lat (ndarray): lateral position (mm)

        Returns:

        """
        import matplotlib.pyplot as plt
        import numpy as np

        axInd = np.min(np.where(self.axial >= axial))
        latInd = np.min(np.where(self.lat >= lat))
        plt.plot(self.t, self.arfidata[axInd, latInd, :])
        plt.xlabel('Time (ms)')
        plt.ylabel('Displacement (\mum)')
        plt.title('Axial = {:.1f} mm, Lateral = {:.1f} mm'.
                  format(self.axial[axInd], self.lat[latInd]))
        plt.show()

        return

    def play(self, timerange):
        """play an animation

        Strongly recommend not stepping though each timesteps; use some skips!

        Args:
            timerange (range): range generator of time steps to animate

        Returns:

        """
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

        fig = plt.figure()

        plt.pcolormesh(self.lat, self.axial, self.arfidata[:, :, 0])
        plt.axes().set_aspect('equal')
        plt.gca().invert_yaxis()
        plt.xlabel('Lateral (mm)')
        plt.ylabel('Axial (mm)')

        anim = animation.FuncAnimation(fig, self.animate, frames=timerange,
                                       blit=False)

        plt.show()

    def animate(self, i):
        import matplotlib.pyplot as plt
        plt.pcolormesh(self.lat, self.axial, self.arfidata[:, :, i])
        plt.title('t = {:.2f} ms'.format(self.t[i]))
