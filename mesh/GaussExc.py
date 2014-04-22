#!/usr/bin/python
# GaussExc.py

__author__ = "Mark Palmeri (mlp6)"
__date__ = "2010-05-19"
__version__ = "20120827"
#__version__ = "20100520"

###########################################################################################
# 20100520
#   * consolidated sigmas into one input tuple
#   * corrected need for abs value on the symmetry searches
#   * corrected the Guassian amplitude calculation to actually include the sigmas!
#   * converted the 'fields' read from the nodefile to floats right off the bat
###########################################################################################
# 2012-08-27 (Palmeri)
#   * Added 'none' symmetry option in case no symmetry is being used in the model
#
###########################################################################################
 
import os
import sys
import math
#import pdb
from optparse import OptionParser

def main():
    parser = OptionParser(usage="Generate *LOAD_NODE_POINT data with Gaussian weighting about dim1 = 0, dim2 = 0, extending through dim3.  All spatial units are in the unit system for the node definitions.\n\n%prog [OPTIONS]...",version="%s" % __version__)
#    parser = OptionParser(usage="Generate *LOAD_NODE_POINT data with Gaussian weighting about dim1 = 0, dim2 = 0, extending through dim3.  All spatial units are in the unit system for the node definitions.\n\n%prog [OPTIONS]...", version="%prog %s" % __version__)
    parser.add_option("--nodefile",dest="nodefile",help="Node definition file (*.dyn) [default = %default]",default="nodes.dyn")
    parser.add_option("--sigma",dest="sigma",type="float",help="Standard devisions in 3 dims [default = %default]",nargs=3,default=(1.0,1.0,1.0))
    parser.add_option("--amp",dest="amp",type="float",help="Peak Gaussian amplitude [default = %default]",default=1.0)
    parser.add_option("--amp_cut",dest="amp_cut",type="float",help="Cutoff from peak amplitude to discard (so a lot of the nodes don't have neglible loads on them) [default = %default]",default=0.05)
    parser.add_option("--center",dest="center",type="float",help="Gaussian center [default = %default]",nargs=3,default=(0.0,0.0,-2.0))
    parser.add_option("--search_tol",dest="search_tol",type="float",help="Node search tolerance [default = %default]",default=0.0001)
    parser.add_option("--sym",dest="sym",type="string",help="Mesh symmetry (qsym or hsym) [default = %default]",default="qsym")

    (opts,args) = parser.parse_args()

    #pdb.set_trace()
    # setup the new output file with a very long, but unique, filename
    loadfilename = "gauss_exc_sigma_%.3f_%.3f_%.3f_center_%.3f_%.3f_%.3f_amp_%.3f_amp_cut_%.3f_%s.dyn" % (opts.sigma[0],opts.sigma[1],opts.sigma[2],opts.center[0],opts.center[1],opts.center[2],opts.amp,opts.amp_cut,opts.sym)
    LOADFILE = open(loadfilename,'w')
    LOADFILE.write("$ Generated using %s (version %s) with the following options:\n" % (sys.argv[0],__version__))
    LOADFILE.write("$ %s\n" % opts)

    LOADFILE.write("*LOAD_NODE_POINT\n")

    # loop through all of the nodes and see which ones fall w/i the Gaussian excitation field
    sym_node_count = 0
    node_count = 0
    NODEFILE = open(opts.nodefile,'r')
    for i in NODEFILE:
        # make sure not to process comment and command syntax lines
        if i[0] != "$" and i[0] != "*":
            i=i.rstrip('\n')
            # dyna scripts should be kicking out comma-delimited data; if not, then the user needs to deal with it
            fields=i.split(',')
            fields = [float(i) for i in fields]
            # check for unexpected inputs and exit if needed (have user figure out what's wrong)
            if len(fields) != 4:
                print("WARNING: An unexpected number of node definition columns encountered!")
                print(fields)
                sys.exit(1)
            # compute the Gaussian amplitude at the node
            exp1 = math.pow((fields[1]-opts.center[0])/opts.sigma[0],2)
            exp2 = math.pow((fields[2]-opts.center[1])/opts.sigma[1],2)
            exp3 = math.pow((fields[3]-opts.center[2])/opts.sigma[2],2)
            nodeGaussAmp = opts.amp * math.exp(-(exp1 + exp2 + exp3))

            # write the point load only if the amplitude is above the cutoff
            # dyna input needs to be limited in precision
            #pdb.set_trace()
            if nodeGaussAmp > opts.amp*opts.amp_cut:
                
                node_count += 1
                # check for quarter symmetry force reduction (if needed)
                if opts.sym == 'qsym':
                    if math.fabs(fields[1]) < opts.search_tol and math.fabs(fields[2]) < opts.search_tol:
                        nodeGaussAmp = nodeGaussAmp/4
                        sym_node_count += 1
                    elif math.fabs(fields[1]) < opts.search_tol or math.fabs(fields[2]) < opts.search_tol:
                        nodeGaussAmp = nodeGaussAmp/2
                        sym_node_count += 1
                # check for half symmetry force reduction (if needed)
                elif opts.sym == 'hsym':
                    if math.fabs(fields[1]) < opts.search_tol:
                        nodeGaussAmp = nodeGaussAmp/2
                        sym_node_count += 1
                elif opts.sym != 'none':
                    sys.exit('ERROR: Invalid symmetry option specified.')

                LOADFILE.write("%i,3,1,-%.4f\n" % (int(fields[0]),nodeGaussAmp))
                
    # wrap everything up
    NODEFILE.close()
    LOADFILE.write("*END\n")
    LOADFILE.write("$ %i loads generated\n" % node_count)
    LOADFILE.write("$ %i exist on a symmetry plane / edge\n" % sym_node_count)
    LOADFILE.close()
 
if __name__ == "__main__":
    main()
