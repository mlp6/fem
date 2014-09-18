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


Release Notes
=============

v0.1
 * Old version of FEM code that relied on d3plot* files for result extraction.

v0.1.1
 * Fixed --top designation in mesh/bc.py
