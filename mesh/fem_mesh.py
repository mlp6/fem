"""
fem_mesh.py

Generic functions for all meshing functions
"""

__author__ = "Mark Palmeri"
__email__ = "mlp6@duke.edu"
__version__ = "20140129"


def check_version():
    """
    Check that at least python2.7 is being used, and recommend upgrading to
    python3 if 2.bit_length(x is being used
    """
    import sys

    if sys.version_info[:2] < (2, 7):
        sys.exit("ERROR: Requires Python >= 2.7")

    if sys.version_info[0] < 3:
        print("WARNING: It is recommended that you upgrade to python3!")


def strip_comments(nodefile):
    import os
    nodefile_nocmt = '%s.tmp' % nodefile
    os.system("egrep -v '(^\*|^\$)' %s > %s" % (nodefile, nodefile_nocmt))
    return nodefile_nocmt
