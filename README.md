Finite Element Method (FEM) ARF Simulation Code 
===============================================

Python Tools, [Field II](http://field-ii.dk) Intensity Field Solution, LS-DYNA
Pre/Post Processing

All software in this repository is licensed under the Apache v2.0 license, as
detailed in the LICENSE file.

If you are using these simulation tools in work that you publish, then please
consider citing the following manuscript:

[Palmeri ML, Sharma AC, Bouchard RR, Nightingale RW, Nightingale KR.  "A
Finite-Element Method Model of Soft Tissue Response to Impulsive Acoustic
Radiation Force," IEEE UFFC, 52(10): 1699-1712,
2005.](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2818996/)

Installation
============
 * You can locally clone this repository:
 ```
 git clone git@github.com:Duke-Ultrasound/fem.git
 ```

 This approach will work if you have an [SSH
 key](https://help.github.com/articles/generating-ssh-keys) uploaded to GitHub.
 If not, then you can also clone the reportory using:
 ```
 git clone https://github.com/Duke-Ultrasound/fem.git
 ```

 * Add the fem subdirectories to your Matlab path.  One approach is to add the
   following to ```$HOME/matlab/startup.m```: 
 ```
 fem_root = 'PATH/TO/GIT/CLONED/fem';
 addpath(fullfile(fem_root, 'mesh'));
 addpath(fullfile(fem_root, 'field'));
 addpath(fullfile(fem_root, 'post'));
 ```
 where ```fem_root``` is the path of your git-cloned fem repository.

 * There is a ```probes``` submodule available to restricted institutions.  If
   you do not have access to that repository, then you can use
   ```field/linear.m``` and ```field/curvilinear.m``` as starting points to
   define transducers.  If you do have access, then you can initialize the
   submodule using ```git submodule init``` followed by ```git submodule
   update```.

 * All of the python scripts have help available using the ```--help``` flag.


Code Layout
===========

This repository contains 3 subdirectories of code:

 1. ```mesh```: scripts to generate meshes, apply boundary conditions and
    simple loads ([mesh/README.md](mesh/README.md))
 2. ```field```: [Field II](http://field-ii.dk) scripts to simulate acoustic
    radiation force excitations to impose as point loads on your model.  The
    ```probes``` submodule can be utilized with these scripts
    ([field/README.md](field/README.md))
 3. ```post```: scripts to post-process LS-DYNA output for processing /
    visualization in ls-prepost, Matlab, and Paraview
    ([post/README.md](post/README.md))

Please see the ```README.md``` files in each respective subdirectory for more
detailed descriptions of the available scripts.

Coordinate & Unit Conventions
=============================

 * The mesh (LS-DYNA) and Field II spatial axis conventions are different (this
   is unfortunate, but maintained for legacy compatibility).

 * LS-DYNA and mesh-related tools use a rotated, right-hand rule coorindate
   system: 
   + Axial extends into -z, 
   + Lateral extends into +y, 
   + Elevation extends into -x.

 * LS-DYNA is run unitless, but scripts assume and scale quantitites assuming a
   CGS unit system.

 * Field II tools a standard, right-hand rule coordinate system:
   + Axial extends into +z, 
   + Lateral extends into +x, 
   + Elevation extends into +y.

 * Field II internally uses MKS units, but scripts will specify units on the
   inputs


Testing
=======
There are test scripts / models available for code validation and future
development ([test/README.md](test/README.md)).  Please use existing tests if
fixing bug / editing existing features, or create new tests for new features.
Ipython notebooks documenting testing, performance, etc. are also saved in some
of the testing directories.

Contributors
============
 * Mark Palmeri (mlp6@duke.edu)
 * Ningrui Li (nl91@duke.edu)
 * Mallory Selzo (UNC-CH)
 * Chris Moore (chrisjmoore@unc.edu)
 * David Bradway (david.bradway@duke.edu)
 * Nick Bottenus (nbb@duke.edu)
