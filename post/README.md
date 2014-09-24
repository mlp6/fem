fem/post
=========

Python scripts to generate result files for use in Matlab and the
[https://github.com/Duke-Ultrasound/ultratrack.git](ultratrack) simulation
tools.

 * **create_disp_dat.py:** Generate a binary ```disp.dat``` file (used by
   ```ultratrack```) and/or a VTK results file (used by Paraview).

 * **create_res_sim_mat.py:** Generate a ```res_sim.mat``` file from
   ```disp.dat``` that has ARFI result file-formatted imaging plane
   displacement data.

 * **res_sim.mat:** Created by ```create_res_sim_mat.py``` and contains:
   + ```arfidata```: 3D matrix of z-displacement data (microns) in the imaging
     plane (axial x lateral x time)
   + ```axial```: axis (mm)
   + ```lat```: axis (mm)
   + ```t```: time (s)
