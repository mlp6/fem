See the git commit history for an effective change log pre-v6.3.1

v6.4.0
======
* Add ``ResSim`` post-processing class (``post/res_sim.py``)

v6.5.0
======
* Update ``TopLoad`` from CLI script to python module
* Update ``examples/compress_cube/explicit/`` for latest tools
* Allow BCs to be applied to nodes/faces without imposing non-reflecting / PML faces

v6.5.3
======
* Fix CreateStructure load_elems import error

v6.6.0
======
* Update `post/create_disp_dat.create_dat` docstring
* Re-arrange the example directory structure and add READMEs
* Add `create_disp_dat` unit tests and accelerations
* Add `create_res_sim_mat` unit tests and accelerations
* Improve relative import paths for unit testing, making OS-agnostic

v6.6.1
======
* PEP8 compliance for all active modules (added to unit tests)
* Fixed relative import paths for unit testing across all platforms

v6.7.0
======
* Add Tukey axial weighting of Guassian excitations to achieve more cylindrical shear wave fronts.
* Add more control of parallel threads and memory usage in `field2dyna`.

v6.8.0
======
* Add conda `environment.yml` configuration file to create virtualenv (can use pip or conda).
* Add C/SWIG accessible `post/create_disp_dat_c/create_disp_dat` tool (~8x speedup on large `nodout` files).

v6.8.1
======
* Update `setup.py` and `setup.cfg` for PyPI upload.

v6.8.2
======
* Fix float -> int formatting for `fprint`.

v6.9.0
=======
* Add angled point loads (for phased excitations)
* Fix issue #21: `create_res_sim_mat.py` image plane extraction
* Fix `py.test` issues with `tmpdir` fixtures
* Add ASCII VTK scalar and vector file generation
