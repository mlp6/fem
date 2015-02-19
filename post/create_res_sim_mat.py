'''
create_res_sim_mat.py

Create res_sim.mat file from disp.dat (This was originally called
from StructPost, but now is a stand-alone Python script.)

Copyright 2015 Mark L. Palmeri (mlp6@duke.edu)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

__author__ = "Mark Palmeri"
__email__ = "mlp6@duke.edu"
__license__ = "Apache v2.0"


def main():
    import os
    import sys
    import fem_mesh

    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    args = read_cli()

    mat_tmp_run = 'runmatlab.m'
    matfile = open(mat_tmp_run, 'w')
    matfile.write('addpath(\'%s\');\n' % args.fempath)
    matfile.write('createsimres(\'%s\',\'%s\',\'%s\');\n' % (args.dispout,
                                                             args.nodedyn,
                                                             args.dynadeck))
    matfile.close()

    os.system('matlab -nodesktop -nosplash < runmatlab.m')

    if not os.path.exists(args.ressim):
        sys.exit('ERROR: %s not successfully created' % args.ressim)

    fem_mesh.rm_tmp_file(mat_tmp_run)


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
                     default="/home/mlp6/git/fem/post")
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
