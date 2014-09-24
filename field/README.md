fem/field
=========

All of these functions are used in Matlab (not python).

 * **field2dyna.m:** Primary function to read in node data and solve for the
   intensities at each node for a user-defined focal configuration and
   attenuation.  This will create a ```dyna*.mat``` file.

 * **makeLoadsTemps.m:** Converts the intensities from ```field2dyna.m``` into
   point loads applied at nodes (```PointLoads*.dyn```) and initial
   temperatures (```InitTemp*.dyn```) for thermal safety simulations.
