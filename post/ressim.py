class ResSim:
    """plot and animate res_sim.mat simulation data

    Attributes:
        filename (str): name of file to load in (MATv5)
        arfidata (float ndarray): arfidata
        axial (float ndarray): depth
        lat (float ndarray): lateral
        t (float ndarray): time
        time_scale_factor (float): time scale factor (e.g., s -> ms)
        disp_scale_factor (float): displacement scale factor

    """

    def __init__(self, filename="res_sim.mat"):
        self.filename = filename
        self.lat = None
        self.axial = None
        self.t = None
        self.arfidata = None
        self.time_scale_factor = 1e3  # s -> ms
        self.disp_scale_factor = 1.0

        self.load()

    def load(self):
        """load MATv5 data

        Args:
            filename (str): input filename

        Todo:
            * Make compatible with v7.3 (HDF5) format files.

        """
        from scipy.io import loadmat

        try:
            d = loadmat(self.filename)
        except:
            print(f'{self.filename} most likely not MATv5 format')

        self.lat = d['lat'].squeeze()
        self.axial = d['axial'].squeeze()
        self.t = d['t'].squeeze() * self.time_scale_factor
        self.arfidata = d['arfidata'] * self.disp_scale_factor

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

        """
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots()

        axes.pcolormesh(self.lat, self.axial, self.arfidata[:, :, timestep])
        axes.set_aspect('equal')
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        if title is None:
            axes.set_title(f't = {self.t[timestep]:.2f} ms')
        else:
            axes.set_title(title)
        axes.invert_yaxis()
        if save:
            filename = f'{savename}_{timestep:04d}.png'
            fig.savefig(filename)
            print(f'Saved plot: {filename}')
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

    def play(self, timerange):
        axes.plot(self.t, self.arfidata[axInd, latInd, :])
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        if title is None:
            axes.set_title(f'Axial = {self.axial[axInd]:.1f} mm, Lateral = {self.lat[latInd]:.1f} mm')
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
        plt.title(f't = {self.t[i]:.2f} ms')
