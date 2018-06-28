# this is an example of an older, CLI-based run script
python3 ../../mesh/GenMesh.py --xyz -0.5 0.0 0.0 1.0 -3.0 0.0 --numElem 50 100 300
python3 ../../mesh/bc.py
matlab -nodesktop -nosplash -r "run_field; ...
                                makeLoadsTemps('dyna-I-f7.20-F1.0-FD0.020-a0.50.mat', ...
                                'dyna-I-f7.20-F1.0-FD0.020-a0.50.mat', ...
                                1000,400,4.2,0.01^3,'q',1); quit;"
ls-dyna-d ncpu=2 i=vf105.dyn
python3 ../../post/create_disp_dat.py
python3 ../../post/create_res_sim.py --dynadeck vf105.dyn 
