"""
:mod:`GaussExc` -- Gaussian excitation
======================================

.. module:: GauseExc
   :synopsis: generate Gaussian distribution of point loads
   :license: Apache v2.0, see LICENSE for details
   :copyright: Copyright 2016 Mark Palmeri

.. moduleauthor:: Mark Palmeri <mlp6@duke.edu>
"""

from __future__ import absolute_import
from __future__ import print_function


def main():
    """ Generate Gaussian-weighted point load distribution
    """
    from fem_mesh import check_version
    check_version()

    import sys

    opts = read_cli()

    # setup the new output file with a very long, but unique, filename
    loadfilename = ("gauss_exc_sigma_%.3f_%.3f_%.3f_"
                    "center_%.3f_%.3f_%.3f_amp_%.3f_amp_cut_%.3f_%s.dyn" %
                    (opts.sigma[0], opts.sigma[1], opts.sigma[2],
                     opts.center[0], opts.center[1], opts.center[2],
                     opts.amp, opts.amp_cut, opts.sym))
    LOADFILE = open(loadfilename, 'w')
    LOADFILE.write("$ Generated using %s:\n" % sys.argv[0])
    LOADFILE.write("$ %s\n" % opts)

    LOADFILE.write("*LOAD_NODE_POINT\n")

    # loop through all of the nodes and see which ones fall w/i the Gaussian
    # excitation field
    NODEFILE = open(opts.nodefile, 'r')
    for i in NODEFILE:
        # make sure not to process comment and command syntax lines
        if i[0] != "$" and i[0] != "*":
            i = i.rstrip('\n')
            # dyna scripts should be kicking out comma-delimited data; if not,
            # then the user needs to deal with it
            fields = i.split(',')
            fields = [float(j) for j in fields]
            # check for unexpected inputs and exit if needed (have user figure
            # out what's wrong)
            # TODO: Do I want this to check each time?  Looks like it could
            #       slow things down on really large files
            check_num_fields(fields)

            # compute the Gaussian amplitude at the node
            nodeGaussAmp = calc_gauss_amp(fields, opts.center, opts.sigma,
                                          opts.amp)

            # write the point load only if the amplitude is above the cutoff
            # dyna input needs to be limited in precision
            if nodeGaussAmp > opts.amp*opts.amp_cut:

                nodeGaussAmp = sym_scale_amp(fields, nodeGaussAmp,
                                             opts.sym, opts.search_tol)

                LOADFILE.write("%i,3,1,-%.4f\n" % (int(fields[0]),
                                                   nodeGaussAmp))

    # wrap everything up
    NODEFILE.close()
    LOADFILE.write("*END\n")
    LOADFILE.close()


def check_num_fields(fields):
    """check for 4 fields

    :param fields: list (node ID, x, y, z)
    """
    from sys import exit
    if len(fields) != 4:
        raise SyntaxError("Unexpected number of node columns")
        exit(1)
    else:
        return 0


def sym_scale_amp(fields, nodeGaussAmp, sym, search_tol=0.0001):
    """scale point load amplitude on symmetry faces / edges

    :param fields: list (node ID, x, y, z)
    :param nodeGaussAmp: amplitude of point load
    :param sym: type of mesh symmetry (none, qsym, hsym)
    :param search_tol: spatial tolerance to find nearby nodes
    :returns nodeGaussAmp: symmetry-scaled point load amplitude
    """
    from math import fabs
    import sys

    if sym == 'qsym':
        if (fabs(fields[1]) < search_tol and fabs(fields[2]) < search_tol):
            nodeGaussAmp = nodeGaussAmp/4
        elif (fabs(fields[1]) < search_tol or fabs(fields[2]) < search_tol):
            nodeGaussAmp = nodeGaussAmp/2
    elif sym == 'hsym':
        if fabs(fields[1]) < search_tol:
            nodeGaussAmp = nodeGaussAmp/2
    elif sym != 'none':
        sys.exit('ERROR: Invalid symmetry option specified.')

    return nodeGaussAmp


def calc_gauss_amp(node_xyz, center, sigma, amp):
    """calculated the Gaussian amplitude at the node

    :param: node_xyz (list of x,y,z node coordinates)
    :param: center (list of x,y,z for Gaussian center)
    :param: sigma (list of x,y,z Guassian width)
    :param: amp (peak Gaussian source amplitude)
    :returns nodeGaussAmp: point load amplitude at the specified node
    """
    from math import pow, exp
    exp1 = pow((node_xyz[1]-center[0])/sigma[0], 2)
    exp2 = pow((node_xyz[2]-center[1])/sigma[1], 2)
    exp3 = pow((node_xyz[3]-center[2])/sigma[2], 2)
    nodeGaussAmp = amp * exp(-(exp1 + exp2 + exp3))

    return nodeGaussAmp


def read_cli():
    """ read CLI arguments
    """
    import argparse as ap

    p = ap.ArgumentParser(description="Generate *LOAD_NODE_POINT data "
                          "with Gaussian weighting about dim1 = 0, "
                          "dim2 = 0, extending through dim3.  All "
                          "spatial units are in the unit system for the "
                          "node definitions.",
                          formatter_class=ap.ArgumentDefaultsHelpFormatter)
    p.add_argument("--nodefile",
                   help="Node definition file (*.dyn)",
                   default="nodes.dyn")
    p.add_argument("--sigma",
                   type=float,
                   help="Standard devisions in 3 dims",
                   nargs=3,
                   default=(1.0, 1.0, 1.0))
    p.add_argument("--amp",
                   type=float,
                   help="Peak Gaussian amplitude",
                   default=1.0)
    p.add_argument("--amp_cut",
                   type=float,
                   help="Cutoff from peak amplitude to discard (so a lot "
                   "of the nodes don't have negligible loads on them)",
                   default=0.05)
    p.add_argument("--center",
                   type=float,
                   help="Gaussian center",
                   nargs=3,
                   default=(0.0, 0.0, -2.0))
    p.add_argument("--search_tol",
                   type=float,
                   help="Node search tolerance",
                   default=0.0001)
    p.add_argument("--sym",
                   help="Mesh symmetry (qsym or hsym)",
                   default="qsym")

    opts = p.parse_args()

    return opts

if __name__ == "__main__":
    main()
