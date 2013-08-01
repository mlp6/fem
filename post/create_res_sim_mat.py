#!/usr/local/bin/python2.7
'''
create_res_sim_mat.py - create res_sim.mat file from disp.dat

This was originally called from StructPost, but now is a stand-along Python script
'''

__author__ = "Mark Palmeri (mlp6)"
__date__ = "2013-01-01"
__modified__ = "2013-01-01"
__email__ = "mark.palmeri@duke.edu"

def main():
    import os,sys
    
    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate res_sim.mat from disp.dat",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--dispout",help="name of the binary displacement output file",default="disp.dat")
    parser.add_argument("--ressim",help="name of the matlab output file",default="res_sim.mat")
    parser.add_argument("--fempath",help="path to the FEM post-processing scripts",default="/radforce/mlp6/fem/post")
    parser.add_argument("--nodedyn",help="ls-dyna node definition file",default="nodes.dyn")
    parser.add_argument("--dynadeck",help="ls-dyna input deck",default="dynadeck.dyn")

    args = parser.parse_args()
    dispout = args.dispout
    ressim = args.ressim
    fempath = args.fempath
    nodedyn = args.nodedyn
    dynadeck = args.dynadeck

    matfile = open('runmatlab.m','w')
    matfile.write('addpath(\'%s\');\n' % fempath)
    matfile.write('createsimres(\'%s\',\'%s\',\'%s\');\n' % (dispout,nodedyn,dynadeck))
    matfile.close()

    os.system('matlab -nodesktop -nosplash < runmatlab.m')

    if not os.path.exists(ressim):
        sys.exit('ERROR: %s not successfully created' % ressim) 

if __name__ == "__main__":
    main()
