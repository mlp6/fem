#!/usr/local/bin/python2.7

import os, sys
import argparse

__author__ = "Mark Palmeri"
__date__ = "2010-12-16"
__version__ = "0.1"

parser = argparse.ArgumentParser(description="Find result files missing from all subdirectories in the specified root directory.  \n\nPROG [OPTIONS]...",version="%s" % __version__)

parser.add_argument("--root",dest="simroot",help="root path for sim subdirs [default = %default]",default=".")
parser.add_argument("--sdir",dest="sdir",help="suffix to define relevant sim subdirectories [default = %default]",default="mm")
parser.add_argument("--res",dest="res",help="res file name [default = %default]",default="res_sim.mat")

args = parser.parse_args()

if not os.path.exists(args.simroot):
    sys.exit('ERROR: %s does not exist' % args.simroot)

print('%s is missing from the following subdirectories in %s :' % (args.res,args.simroot))
for root, dirs, files in os.walk(args.simroot):
    if root.endswith(args.sdir):
        if not files.__contains__(args.res):
            print(' %s' % root)
