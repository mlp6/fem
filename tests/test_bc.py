"""test_bc.py
"""

import sys

import os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../mesh/')

def test_axisspacing():
    """node spacing along each axis
    """
    from bc import axis_spacing
    axes = [[0, 0.1], [1, 1.1], [2.1, 2.2]]
    axdiff = axis_spacing(axes)

    assert round(axdiff[0] - 0.1, 3) == 0
    assert round(axdiff[1] - 0.1, 3) == 0
    assert round(axdiff[2] - 0.1, 3) == 0


def test_topplane():
    """TODO
        """
    pass


def test_bottomplane():
    """TODO
        """
    pass


def find_hsymface():
    """TODO
        """
    pass


def find_qsymfaces():
    """TODO
        """
    pass


def find_qsymedge():
    """TODO
        """
    pass


def assign_pml():
    """TODO
        """
    pass