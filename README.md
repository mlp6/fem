Finite Element Modeling (FEM) Code 
==================================

Python Tools, Field II Intensity Field Solution, LS-DYNA Pre/Post Processing

This repository was managed via svn until 2013-04-22; migrated to GitHub for
active management.  All software in this repository is licensed under the MIT
license, as detailed in the LICENSE file.

If you are using these simulation tools in work that you publish, then please
consider citing the following manuscript:

*Palmeri ML, Sharma AC, Bouchard RR, Nightingale RW, Nightingale KR.  "A
Finite-Element Method Model of Soft Tissue Response to Impulsive Acoustic
Radiation Force," IEEE UFFC, 52(10): 1699-1712, 2005. [PMCID: 16382621]*


RELEASE NOTES
=============

v0.1 (2012-11-02)
 * Old version of FEM code that relied on d3plot* files for result extraction.

v0.2a
 * FEM results are extracted from ASCII nodout files
 * New GenMesh.py script to make reclinear mesh generation independent of lspp4
