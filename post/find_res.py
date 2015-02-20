'''
find_res.py
'''

__author__ = "Mark Palmeri"
__email__ = "mlp6@duke.edu"
__date__ = "2010-12-16"
__modified__ = "2014-06-03"

def main():
    '''
    check for existing/missing result files in downstream directories
    '''
    args = read_cli()

    check_simroot(args)

    display_status(args)

    walk_n_find(args)


def read_cli():
    '''
    read in optional CLI arguments
    '''
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
                   help="find missing, instead of existing, results",
                   action='store_true')
    p.set_defaults(missing=False)

    args = p.parse_args()

    return args

def check_simroot(args):
    '''
    check if the simulation root directory exists
    '''
    import os
    import sys

    if not os.path.exists(args.simroot):
        sys.exit('ERROR: %s does not exist' % args.simroot)


def display_status(args):
    '''
    display what is going on
    '''
    if args.missing:
        print_msg = 'missing from'
    else:
        print_msg = 'in'

    print(('%s is %s the following %s subdirs in %s :' % (args.res, print_msg,
                                                         args.sdir,
                                                         args.simroot)))

def walk_n_find(args):
    '''
    walk simroot and look for res files in specified sdirs
    '''
    import os

    for root, dirs, files in os.walk(args.simroot):
        if args.sdir in os.path.basename(root):
            if args.missing:
                if args.res not in files:
                    print((' %s' % root))
            else:
                if args.res in files:
                    print((' %s' % root))


if __name__ == '__main__':
    main()
