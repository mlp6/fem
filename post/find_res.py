'''
find_res.py
'''

__author__ = "Mark Palmeri"
__email__ = "mlp6@duke.edu"
__date__ = "2010-12-16"
__modified__ = "2014-06-03"

import os
import sys
import argparse

p = argparse.ArgumentParser(description="Find result files missing from "
                                 "all specified subdirectories in the "
                                 "specified root directory.")

p.add_argument("--root",
               dest="simroot",
               help="root path for sim subdirs [default = .]",
               default=".")
p.add_argument("--sdir",
               dest="sdir",
               help="string  to define relevant sim subdirectories "
               "[default = mm]", default="mm")
p.add_argument("--res",
               dest="res",
               help="res file name [default = res_sim.mat]",
               default="res_sim.mat")

p.add_argument("--missing",
               dest="missing",
               help="find if the result files are missing instead of existing",
               default=False)

args = p.parse_args()

if not os.path.exists(args.simroot):
    sys.exit('ERROR: %s does not exist' % args.simroot)

print('%s is missing from the following %s subdirectories in %s :' %
      (args.res, args.sdir, args.simroot))

for root, dirs, files in os.walk(args.simroot):
    if args.sdir in os.path.basename(root):
        if args.res not in files:
            print(' %s' % root)
