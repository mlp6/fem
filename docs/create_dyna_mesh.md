Creating rectilinear meshes for LS-DYNA
========================================

Most of the meshes used in first-pass FEM simulations of acoustic radiation
force excitations are large rectangular solids with either uniform cubic 3D
elements, or elements with a slight aspect ratio.  This document provides an
overview of the process of generating a 3D mesh using tools in this repository
(```fem/mesh```).

SYNTAX
------
```mesh/GenMesh.py``` will generate a the rectilinear mesh with user-specified
properties.  You can specify two opposing corner vertices of the mesh (```--n1``` and
```--n2```), the element density on each edge (x, y, z), and the names of the output
files for node and element definitions.  

Run: ```python GenMesh.py --help``` for detailed input syntax.

COORDINATE SYSTEM
-----------------
Meshes in this code base utilize different conventions for the FEM portion of
the code compared to the Field II simulation component.  LS-DYNA mesh
conventions are:

 * x - elevation 
 * y - lateral
 * z - axial (negative, with transducer face @ z = 0)

Maintaining a right-hand rule convention, for a quarter-symmetry model, x would
span a negative range of values for positive 7 values.  

UNITS
-----
The typical unit system for the mesh is CGS, and this will be assumed in the
code that passes data to/from Field II.

NEXT STEPS
----------
1. Your mesh will be used as an input to Field II to simulate the acoustic
radiation force at nodes.  This is done using ```field/field2dyna```.

2. You will need to generate boundary conditions for your mesh (```mesh/bc.py```)

3. You may want to create structures in your mesh with different material
properties (```mesh/CreateStructure.py```)

