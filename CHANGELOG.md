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
* Update post/create_disp_dat.create_dat docstring
* Re-arrange the example directory structure and add READMEs
* Add create_disp_dat unit tests and accelerations
* Add create_res_sim_mat unit tests and accelerations
* Improve relative import paths for unit testing, making OS-agnostic
