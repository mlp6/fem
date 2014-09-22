Finite Element Modeling (FEM) Code 
==================================

Python Tools, Field II Intensity Field Solution, LS-DYNA Pre/Post Processing

This repository was managed via svn until 2013-04-22; migrated to GitHub for
active management.  All software in this repository is licensed under the
Apache v2.0 license, as detailed in the LICENSE file.

If you are using these simulation tools in work that you publish, then please
consider citing the following manuscript:

*Palmeri ML, Sharma AC, Bouchard RR, Nightingale RW, Nightingale KR.  "A
Finite-Element Method Model of Soft Tissue Response to Impulsive Acoustic
Radiation Force," IEEE UFFC, 52(10): 1699-1712, 2005. [PMCID: 16382621]*


Installation
============
 * You can locally clone this repository:
 ```
 git clone git@github.com:Duke-Ultrasound/fem.git
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
   submodule using ``git submodule init``` followed by ```git submodule
   update```.

 * All of the python scripts have help available using the ```--help``` flag.


Coordinate & Unit Conventions
=============================

 * The mesh (LS-DYNA) and Field II spatial axis conventions are different (this
   is unfortunate, but maintained for legacy compatibility).

 * LS-DYNA uses a rotated, right-hand rule coorindate system, where axial
   extended into -z, lateral is +y, and elevation is -x.

 * Field II has axial extended into +z, lateral is +x, and elevation is +y.

 * Field II internally uses MKS units, but scripts will specify units on the
   inputs

 * LS-DYNA is run unitless, but scripts assume and scale quantitites assumine a
   CGS unit system.

Code Layout
===========

This repository contains 3 subdirectories of code:

 1. ```mesh```: scripts to generate meshes, apply boundary conditions and
    simple loads [mesh/README.md](mesh/README.md)
 2. ```field```: Field II scripts to simulate acoustic radiation force
    excitations to impose as point loads on your model.  The ```probes```
    submodule can be utilized with these scripts.
 3. ```post```: scripts to post-process LS-DYNA output for processing /
    visualization in ls-prepost, Matlab, and Paraview

Please see the ```README.md``` files in each respective subdirectory for more
detailed descriptions of the available scripts.
