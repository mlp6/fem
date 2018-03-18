class ResSim:
    """plot and animate res_sim.mat simulation data"""

    def __init__(self, filename="res_sim.mat"):
        self.load(filename)

    def load(self, filename, time_scale_factor=1e3, disp_scale_factor=1.0):
        """load MATv5 data

        Args:
            filename (str): input filename
            time_scale_factor (float): time scale factor (e.g., s -> ms)
            disp_scale_factor (float): displacement scale factor

        Returns:
            attributes (ndarray): [lat, axial, t, arfidata]

        """
        from scipy.io import loadmat

        d = loadmat(filename)

        self.lat = d['lat'].squeeze()
        self.axial = d['axial'].squeeze()
        self.t = d['t'].squeeze() * time_scale_factor
        self.arfidata = d['arfidata'] * disp_scale_factor

    def plot(self, timestep, show=True, save=False, savename='file',
             xlabel='Lateral (mm)', ylabel='Axial (mm)', title=None):
        """Plot arfidata at specified timestep.

        Args:
            timestep (int):
            show (Boolean): show plot
            save (Boolean): save PNG (objectname_timestep.png)
            savename (str): saved PNG filename prefix
            xlabel (str):
            ylabel (str):
            title (str):

        Returns:

        """
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots()

        axes.pcolormesh(self.lat, self.axial, self.arfidata[:, :, timestep])
        axes.set_aspect('equal')
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        if title is None:
            axes.set_title('t = {:.2f} ms'.format(self.t[timestep]))
        else:
            axes.set_title(title)
        axes.invert_yaxis()
        if save:
            filename = '{}_{:04d}.png'.format(savename, timestep)
            fig.savefig(filename)
            print('Saved plot: {}'.format(filename))
        if show:
            fig.show()

    def timeplot(self, axial, lat, xlabel='Time (ms)',
                 ylabel='Displacement (\mum)', title=None, show=True):
        """plot arfidata through time at specified ax and lat position (mm)

        Args:
            axial (ndarray): axial depth (mm)
            lat (ndarray): lateral position (mm)
            xlabel (str):
            ylabel (str):
            title (str):
            show (Boolean): show the plot

        Returns:

        """
        import matplotlib.pyplot as plt
        import numpy as np

        fig, axes = plt.subplots()

        axInd = np.min(np.where(self.axial >= axial))
        latInd = np.min(np.where(self.lat >= lat))

        axes.plot(self.t, self.arfidata[axInd, latInd, :])
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        if title is None:
            axes.set_title('Axial = {:.1f} mm, Lateral = {:.1f} mm'.
                           format(self.axial[axInd], self.lat[latInd]))
        else:
            axes.set_title(title)

        if show:
            fig.show()

    def play(self, timerange, xlabel='Lateral (mm)', ylabel='Axial (mm)',
             show=True):
        """play an animation

        Strongly recommend not stepping though each timesteps; use some skips!

        Args:
            timerange (range): range generator of time steps to animate
            xlabel (str):
            ylabel (str):
            show (Boolean): show animation

        Returns:

        Todo:
            * Add save option

        """
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

        fig, axes = plt.subplots()

        axes.pcolormesh(self.lat, self.axial, self.arfidata[:, :, 0])
        axes.set_aspect('equal')
        axes.invert_yaxis()
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)

        anim = animation.FuncAnimation(fig, self.animate, frames=timerange,
                                       blit=False)

        if show:
            fig.show()

    def animate(self, i):
        import matplotlib.pyplot as plt
        plt.pcolormesh(self.lat, self.axial, self.arfidata[:, :, i])
        plt.title('t = {:.2f} ms'.format(self.t[i]))
