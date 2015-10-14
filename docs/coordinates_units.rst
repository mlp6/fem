Coordinate & Unit Conventions
=============================

-  The mesh (LS-DYNA) and Field II spatial axis conventions are
   different (this is unfortunate, but maintained for legacy
   compatibility).

-  LS-DYNA and mesh-related tools use a rotated, right-hand rule
   coorindate system:
-  Axial extends into -z,
-  Lateral extends into +y,
-  Elevation extends into -x.

-  LS-DYNA is run unitless, but scripts assume and scale quantitites
   assuming a CGS unit system.

-  Field II tools a standard, right-hand rule coordinate system:
-  Axial extends into +z,
-  Lateral extends into +x,
-  Elevation extends into +y.

-  Field II internally uses MKS units, but scripts will specify units on
   the inputs
