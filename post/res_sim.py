res = {}
import matplotlib.pyplot as plt
fig = plt.figure()

def load(filename="res_sim.mat"):
    """load MATv5 data

    :param filename:
    :returns: res (dict: lat, axial, t, arfidata)
    """
    from scipy.io import loadmat

    res = loadmat(filename)

    return res


def plot(res, timestep):
    """plot arfidata at specified timestep

    :param resdict: res_sim.mat dict
    :param timestep: int
    """

    plt.axes().set_aspect('equal')
    plt.xlabel('Lateral (mm)')
    plt.ylabel('Axial (mm)')
    plt.gca().invert_yaxis()
    plt.title('{:.2f} ms'.format(res['t'][0, timestep]*1e3))
    plt.pcolormesh(res['lat'], res['axial'].transpose(), res['arfidata'][:, :, timestep])
    plt.show()


def play(res, frames):
    """animate plots

    :param frames: range of timesteps to animate
    """
    from matplotlib.animation import FuncAnimation

    a = FuncAnimation(fig, animate, frames=frames, blit=False)
    plt.show()


def animate(t):
    plt.title('{:.2f} ms'.format(res['t'][0, timestep]*1e3))
    p = plt.pcolormesh(res['lat'], res['axial'].transpose(), res['arfidata'][:, :, timestep])

    return p
