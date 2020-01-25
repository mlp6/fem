"""Generate compression loads on top surface."""
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    """

    TODO: way too complicated for now; refactor this
    """

    opts = read_cli()
    generate_loads(loadtype=opts.loadtype, direction=opts.direction,
                   amplitude=opts.amplitude, lcid=opts.lcid,
                   nodefile=opts.nodefile, top_face=(0, 0, 0, 0, 0, 1))


def generate_loads(loadtype='disp', direction=2, amplitude=-1.0,
                   loadfile='topload.dyn', nodefile='nodes.dyn',
                   top_face=(0, 0, 0, 0, 0, 1), lcid=1):
    """apply loads to

    Args:
        loadtype (str): disp', 'vel', 'accel', 'force'
        direction (int): 0 - x, 1 - y, 2 - z
        amplitude (float): scalar of load type
        loadfile (str): written loadfile name
        nodefile (str):
        top_face (tuple): constraintst to apply
        lcid (int): load curve ID

    Returns:

    """

    planeNodeIDs = extract_top_plane_nodes(nodefile=nodefile, top_face=top_face)
    writeNodeLoads(loadfile, planeNodeIDs, loadtype, direction, amplitude, lcid)


def extract_top_plane_nodes(nodefile, top_face):
    """

    Args:
        nodefile: param top_face:
        top_face:

    Returns:
        planeNodeIDs

    """
    import numpy as np
    from fem.mesh import fem_mesh

    top_face = np.array(top_face)

    nodeIDcoords = fem_mesh.load_nodeIDs_coords(nodefile)
    [snic, axes] = fem_mesh.SortNodeIDs(nodeIDcoords)

    # extract spatially-sorted node IDs on a the top z plane
    axis = int(np.floor(np.divide(top_face.nonzero(), 2)))
    if np.mod(top_face.nonzero(), 2) == 1:
        plane = (axis, axes[axis].max())
    else:
        plane = (axis, axes[axis].min())

    planeNodeIDs = fem_mesh.extractPlane(snic, axes, plane)

    return planeNodeIDs


def writeNodeLoads(loadfile, planeNodeIDs, loadtype, direction,
                   amplitude, lcid):
    """Write load keyword file.

    Args:
        loadfile (str): load filename
        planeNodeIDS (ndarray): array of node IDs
        loadtype (str): disp, vel, accel, force
        direction (int): 0-2
        amplitude (float):
        lcid (int): LCID

    Returns:
        None

    """

    # shift 0-2 -> 1-3
    direction += 1

    with open(loadfile, 'w') as LOADFILE:

        if loadtype == 'disp' or loadtype == 'vel' or loadtype == 'accel':
            LOADFILE.write("*BOUNDARY_PRESCRIBED_MOTION_NODE\n")
        elif loadtype == 'force':
            LOADFILE.write("*LOAD_NODE_POINT\n")
        else:
            logger.error("Invalid load type specified; can only be disp, force, vel or accel.")
            raise ValueError("Invalid load type specified; can only be disp, force, vel or accel.")

        if loadtype == 'disp':
            dofs = f'{direction},2,{lcid},{amplitude:.6f}'
        elif loadtype == 'vel':
            dofs = f'{direction},0,{lcid},{amplitude:.6f}'
        elif loadtype == 'accel':
            dofs = f'{direction},1,{lcid},{amplitude:.6f}'
        elif loadtype == 'force':
            dofs = f'{direction},{lcid},{amplitude:.6f}'

        for i in planeNodeIDs:
            for j in i:
                LOADFILE.write(f"{j},{dofs}\n")

        LOADFILE.write("*END\n")


def read_cli():
    """read CLI args"""
    import argparse as ap

    par = ap.ArgumentParser(description="Generate loading conditions for"
                                        "the top surface of the specified"
                                        " mesh.",
                            formatter_class=ap.ArgumentDefaultsHelpFormatter)
    par.add_argument("--loadfile",
                     help="compression load defintion output file",
                     default="topload.dyn")
    par.add_argument("--nodefile",
                     help="node definition input file",
                     default="nodes.dyn")
    par.add_argument("--loadtype",
                     help="apply nodal prescribed displacements (disp), point "
                     "loads (force), velocity (vel) or acceleration (accel)",
                     default="disp")
    par.add_argument("--amplitude",
                     help="amplitude of load",
                     type=float,
                     default=1.0)
    par.add_argument("--direction",
                     help="direction of load (0 - x, 1 - y, 2 - z)",
                     type=int,
                     default=2)
    par.add_argument("--top_face",
                     help="array with 1 indicating top face"
                          "(xmin, xmax, ymin, ymax, zmin, zmax)",
                     nargs="+",
                     type=int,
                     default=(0, 0, 0, 0, 0, 1)
                     )
    par.add_argument("--lcid",
                     help="Load Curve ID to apply to these loads",
                     default=1)

    opts = par.parse_args()

    return opts

if __name__ == "__main__":
    main()
