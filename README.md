[![DOI](https://zenodo.org/badge/72387361.svg)](https://zenodo.org/badge/latestdoi/72387361)
<a href="https://travis-ci.org/mlp6/fem"><img src="https://travis-ci.org/mlp6/fem.svg?branch=master" /></a>
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Acoustic Radiation Force FEM Tools
Finite Element Method (FEM) tools to simulate acoustic radiation force
excitations and resultant shear wave propagation.

All software in this repository is licensed under the Apache v2.0 license, as
detailed in the LICENSE file.

If you are using the FEM simulation tools in work that you publish, then please
consider citing the following manuscript:

[Palmeri ML, Sharma AC, Bouchard RR, Nightingale RW, Nightingale KR. "A
Finite-Element Method Model of Soft Tissue Response to Impulsive Acoustic
Radiation Force," IEEE UFFC, 52(10): 1699-1712,
2005](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2818996/)

Also please cite the following manuscript if you use [Field
II](http://field-ii.dk):

[J.A. Jensen and N. B. Svendsen: Calculation of pressure fields from
arbitrarily shaped, apodized, and excited ultrasound transducers, IEEE Trans.
Ultrason., Ferroelec., Freq. Contr., 39, pp. 262-267,
1992.](http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=139123)

## Installation
These tools have been developed in a Linux environment, which is the
recommended platform for usage.  Many of the Python and some of the C code will
work on Windows and Mac platforms, but build tools for these systems is not
outlined here and robust testing does not exist for those environments (i.e.,
use at your own risk).  The Python tools require a version >= 3.4; 3.6.x is
recommended.

There are three different methods to use/install this package:
1. *[RECOMMENDED]* Install this with `pipenv` in a local virtualenv: `pipenv install -e 
   git+https://github.com/mlp6/fem.git`.
1. Clone this source directory and manually install it in your local
   virtualenv: `pipenv install -e .`
1. Clone this source directory and work directly with it by defining
   `PYTHONPATH` to include the root directory this repository was cloned into.
   This is the easiest method if you are planning to actively edit/develop the
   codebase.  You can do this on-the-fly for a given interactive `ipython`
   session with syntax like: `PYTHONPATH=$HOME/fem ipython`.

## Documentation
The latest documentation is automatically generated from package docstrings
using Sphinx and can be built in ``docs/``.  That directory also contains
static HTML files that can be included in the documentation, as defined in
`docs/index.rst`.  The documentation synced to the root `docs/` directory level
are also rendered at https://mlp6.github.io/fem/.

To build the documentation:
1. Make sure that `PYTHONPATH` includes the `fem` package.
1. Make sure that the virtualenv in activated, which includes the
   `sphinx-build` package.
1. Within the `docs/` directory: `make html`
1. Run `docs/rsync_build.sh` to bring the newly-built HTML files and associated
   source files into `docs/`.

The Travis CI testing also tests the documentation build with a dummy process.

## Issues
Please file any bug reports, features requests, etc. using the GitHub
[Issues](https://github.com/mlp6/fem/issues).

## Contributors
- Mark Palmeri (mlp6@duke.edu)
- Ningrui Li (nl91@duke.edu)
- Mallory Selzo (UNC-CH)
- Chris Moore (chrisjmoore@unc.edu)
- David Bradway (david.bradway@duke.edu)
- Nick Bottenus (nbb5@duke.edu)
- Brian Bigler (brian.bigler@duke.edu)
- Carl Herickhoff (cdh14@duke.edu)
- Sam Lipman (sll16@duke.edu)
- Anna Knight (aek27@duke.edu)
- Matthew Huber (@matthew-huber)
