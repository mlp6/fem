Mesh Generation, Boundary Conditions and Loading Scripts
========================================================

All scripts can be run as: ```python script.py [--options]```.  The
```--help``` option can be used to get descriptions of all available options
and default values.

Active Scripts
--------------

 * **GenMesh.py:** Generate a uniform, 3D hexahedral mesh with specified spatial
   extent and element density.

 * **bc.py:** Specify boundary conditions on the mesh, including those for quarter-
   and half-symmetry (using LS-DYNA coordinate system).

 * **CreateStructure.py:** Create structure within an existing mesh of specified
   shape, location, size and Part ID.

 * **GaussExc.py:** Create a Gaussian-weighted ARF excitation with specified
   Gaussian width, location and amplitude cutoff.

 * **TopLoad.py:** Create a loading condition on the top suface of the model,
   either prescribed displacement, force, or acceleration.

 * **fem_mesh.py:** This will never be directly run, but it is a module with
   common functions used by several of the scripts.

Legacy Scripts
--------------

The following scripts are maintained for old simulations that are still being used for older projects.

 * **parseElemsNodes.py:** Legacy script to extract ```nodes.dyn``` and
   ```elems.dyn``` input files from a mesh generated in ls-prepost using
   ```MeshGen.cfile```.

 * **MeshGen.cfile**: Example command script to generate a mesh, similar to
   ```GenMesh.py```, but with some quirks (e.g., points at 0 sometimes are not
   printed).  This generates a ```mesh.dyn``` file that is space delimited and
   can be parsed using ```parseElemsNodes.py```.
