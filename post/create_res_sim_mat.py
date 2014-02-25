'''
create_res_sim_mat.py

Create res_sim.mat file from disp.dat / vel.dat
(This was originally called from StructPost, but now is a stand-along Python
script.)

The MIT License (MIT)

Copyright (c) 2014 Mark L. Palmeri

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

__author__ = "Mark Palmeri"
__version__ = "0.2a"
__email__ = "mlp6@duke.edu"
__license__ = "MIT"


def main():
    import os
    import sys

    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    args = read_cli()

    matfile = open('runmatlab.m', 'w')
    matfile.write('addpath(\'%s\');\n' % args.fempath)
    matfile.write('createsimres(\'%s\',\'%s\',\'%s\');\n' % (args.dispout,
                                                             args.nodedyn,
                                                             args.dynadeck))
    matfile.close()

    os.system('matlab -nodesktop -nosplash < runmatlab.m')

    if not os.path.exists(args.ressim):
        sys.exit('ERROR: %s not successfully created' % args.ressim)


def read_cli():
    """
    read in command line arguments
    """

    import argparse as ap

    par = ap.ArgumentParser(description="Generate res_sim.mat from disp.dat",
                            formatter_class=ap.ArgumentDefaultsHelpFormatter)
    par.add_argument("--dispout",
                     help="name of the binary displacement output file",
                     default="disp.dat")
    par.add_argument("--ressim",
                     help="name of the matlab output file",
                     default="res_sim.mat")
    par.add_argument("--fempath",
                     help="path to the FEM post-processing scripts",
                     default="/radforce/mlp6/fem/post")
    par.add_argument("--nodedyn",
                     help="ls-dyna node definition file",
                     default="nodes.dyn")
    par.add_argument("--dynadeck",
                     help="ls-dyna input deck",
                     default="dynadeck.dyn")

    args = par.parse_args()

    return args


if __name__ == "__main__":
    main()

