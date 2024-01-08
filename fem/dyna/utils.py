import logging

import numpy as np

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def format_dyna_number(num, num_len=10):
    """
    Formats a number to fit LS-DYNA fixed card format (10 characters per field and max 80 character line lengths by default). Handles negative and scientific notation numbers.

    Args:
        num (float): Input number to format.
        num_len (int): Maximum length of number.

    Returns:
        str: Formatted number as a string.
    """
    snum = str(num)

    if len(snum) > num_len:
        if num > 0.01:
            snum = f"{num:.8f}"
        elif abs(num) > 0.01:
            snum = f"{num:.7f}"

        if len(snum) > num_len:
            # Convert number to scientific notation
            snum = f"{num:.5E}"

        # If number string is greater than num_len characters, remove leading zeros from exponent
        if len(snum) > num_len:
            base, exponent = snum.split("E")
            sign = exponent[0]
            if exponent[1] == "0":
                exponent = exponent[2]
            else:
                exponent = exponent[1:]
            snum = base + "E" + sign + exponent

        # If number string is still greater than num_len characters, remove precision bits to make it num_len characters long
        if len(snum) > num_len:
            base, exponent = snum.split("E")
            precision_bits_to_remove = len(snum) - num_len
            snum = base[:-precision_bits_to_remove] + "E" + exponent

    return snum


def count_header_comment_skips(nodefile: str):
    """count comments lines to skip before the first keyword (*)

    Args:
      nodefile: node keyword filename

    Raises:
        FileNotFoundError: Cannot open the specified node file.

    Returns:
        count (int): number of comment lines before first keyword

    """
    import re

    node = re.compile(r"\*", re.UNICODE)
    count = 1
    try:
        with open(nodefile) as f:
            for line in f:
                if node.match(line):
                    return count
                else:
                    count = count + 1
    except FileNotFoundError:
        logger.error(f"Cannot open {nodefile}.")
        raise FileNotFoundError(f"Cannot open {nodefile}.")


def check_x0_y0(pos):
    """check model position

    Check to make sure that nodes exist at (x, y) = (0, 0) so that the focus /
    peak of an ARF excitation is captured by the mesh.

    Args:
        pos: node positions

    Raises:
        RuntimeWarning: no (x, y) == (0, 0) position defined

    Returns:
        0/1 (1 = fail)

    """
    if 0.0 not in pos[0] and 0.0 not in pos[1]:
        warning_msg = "Your mesh does not contain nodes at (x, y) = (0, 0); "
        "this could lead to poor representation of your ARF "
        "focus."
        logger.warning(warning_msg)
        raise RuntimeWarning(warning_msg)
        return 1
    else:
        return 0


def calc_node_pos(xyz=(-1.0, 0.0, -1.0, 1.0, -4.0, 0.0), numElem=(20, 20, 20)):
    """Calculate nodal spatial positions based on CLI specs

    Args:
        xyz: xmin, xmax, ymin, ymax, zmin, zmax) (Default value = (-1.0)
        numElem: (xEle, yEle, zEle)

    Returns:
        pos (list) - list of lists containing x, y, and z positions

    Raises:
        ValueError: wrong number of position range limits input
        ValueError: min/max range swapped in input

    """
    # if len(xyz) != 6:
    #     logger.error("Wrong number of position range limits input.")
    #     raise ValueError("Wrong number of position range limits input.")
    #     sys.exit()

    pos = []
    for i, j in enumerate(range(0, 5, 2)):
        minpos = xyz[j]
        maxpos = xyz[j + 1]
        if maxpos < minpos:
            logger.warning("Range values reversed (max -> min); swapping")
            raise ValueError("Range values reversed (max -> min).")
            minpos, maxpos = maxpos, minpos
        ptemp = np.linspace(minpos, maxpos, numElem[i] + 1)
        pos.append(ptemp.tolist())

    # check to make sure nodes fall at (x, y) = (0, 0)
    check_x0_y0(pos)

    return pos
