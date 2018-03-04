Examples
========

All examples are located in ``examples/``, and each example directory should
contain a ``run.sh`` script that contains all of the commands that should setup
and run each of the models.

compress_cube_implicit
----------------------
A simple strain elastography compression model with a 0.5 x 1.0 x 3.0 cm mesh
of hexahedral elements.  0.5% strain is applied as a displacement on the top
surface with a bottom boundary that can move in-plane.  An implicit solver is
used for this model.
