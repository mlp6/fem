python ../../mesh/GenMesh.py --xyz -0.5 0.0 0.0 1.0 -3.0 0.0 --numElem 50 100 300
python ../../mesh/bc.py
matlab -nodesktop -nosplash -r "field2dyna('nodes.dyn',0.5,1.0,[0.0 0.0 0.02],7.2,'vf105','gaussian'); makeLoadsTemps('dyna-I-f7.20-F1.0-FD0.020-a0.50.mat','dyna-I-f7.20-F1.0-FD0.020-a0.50.mat',1000,400,4.2,0.01^3,'q',1); quit;"
ls-dyna-d ncpu=2 i=vf105.dyn
python ../../post/create_disp_dat.py

# Edit the 'fempath' argument in the next line with your /PATH/TO/GIT/REPO/fem/post
# python ../../post/create_res_sim.py --dynadeck vf105.dyn --fempath /home/mlp6/git/fem/post
