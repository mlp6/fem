# CHANGELOG
See the git commit history for an effective change log pre-v6.3.1

## v6.4.0
* Add ``ResSim`` post-processing class (``post/res_sim.py``)

## v6.5.0
* Update ``TopLoad`` from CLI script to python module
* Update ``examples/compress_cube/explicit/`` for latest tools
* Allow BCs to be applied to nodes/faces without imposing non-reflecting / PML faces

## v6.5.3
* Fix CreateStructure load_elems import error

## v6.6.0
* Update `post/create_disp_dat.create_dat` docstring
* Re-arrange the example directory structure and add READMEs
* Add `create_disp_dat` unit tests and accelerations
* Add `create_res_sim_mat` unit tests and accelerations
* Improve relative import paths for unit testing, making OS-agnostic

## v6.6.1
* PEP8 compliance for all active modules (added to unit tests)
* Fixed relative import paths for unit testing across all platforms

## v6.7.0
* Add Tukey axial weighting of Guassian excitations to achieve more cylindrical shear wave fronts.
* Add more control of parallel threads and memory usage in `field2dyna`.

## v6.8.0
* Add conda `environment.yml` configuration file to create virtualenv (can use pip or conda).
* Add C/SWIG accessible `post/create_disp_dat_c/create_disp_dat` tool (~8x speedup on large `nodout` files).

## v6.8.1
* Update `setup.py` and `setup.cfg` for PyPI upload.

## v6.8.2
* Fix float -> int formatting for `fprint`.

## v6.9.0
* Add angled point loads (for phased excitations)
* Fix issue #21: `create_res_sim_mat.py` image plane extraction
* Fix `py.test` issues with `tmpdir` fixtures
* Add ASCII VTK scalar and vector file generation

## v6.9.1
* Fix Sphinx documentation

## v6.10.0
* Working `setup.py` for `pip git+` installs.

## v7.0.0
* Refactor `create_res_sim_mat` to now be `create_res_sim` with more options to
  output HDF5 and PVD timeseries VTR data.  Legacy calls to
  `create_res_sim_mat` syntax (specifically `run()`) should still work, but the
  name of the module has been changed to reflect the new functionality under
  the hood.
* Paraview PVD / VTR (rectilinear grid) timeseries data files can now be
  generated.
* Unit tests for MATv5, HDF5 and PVD/VTR files added.
* General refactoring of code and clean-up for Google Style docstrings.

## v7.0.1
* Fix Sphinx documentation to render Google Style docstrings correctly.

## v7.0.2
* Relax python3 compatibility to now work with >=3.4

## v7.0.3
* Fix writing of PVD XML file.

## v7.1.0
* add more custimization to ResSim methods
* add ability to re-number PVD timeframes
* augment docstrings

## v7.2.0
* shuffle HDF5 data on save for more effective compression
* refactor `create_res_sim.py` for more explicit file closure, detailed
  docstrings
* update installation instructions
* fix ResSim class (`self.filename`)

## v7.3.0
* Add examples, docs and Markdown files to pip setup-installed package.
* Update installation documents to reflect pip / virtualenv practices.

## v7.3.1
* update `setup.py`

## v7.3.2
* add `package_data` to `setup.py` to capture examples and docs in `pip install`

## v7.3.3
* fix syntax in `examples/tukey_gauss_qsym_pml/run.py`

## v8.0.2
* introduce new package directory layout to make tests work by importing the fem package
* default to using `pipenv` `Pipfile` for virtualenv management
* update minimum Python to >= 3.7
* rm legacy Gitlab CI and Docker configurations

## v8.0.3
* fix Matlab JSON probe read
