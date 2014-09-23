python ../../mesh/GenMesh.py --xyz -0.5 0.0 0.0 1.0 -3.0 0.0 --numElem 50 100 300
python ../../mesh/bc.py
matlab -nodesktop -nosplash -r "field2dyna('nodes.dyn',0.5,1.0,[0.0 0.0 0.02],7.2,'vf105','gaussian')"
python ../../post/create_disp_dat.py
python ../../post/create_res_sim_mat.py --dynadeck vf105.dyn
