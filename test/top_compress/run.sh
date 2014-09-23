python ../../mesh/GenMesh.py --xyz -0.5 0.0 0.0 1.0 -3.0 0.0 --numElem 10 20 60
python ../../mesh/bc.py --notop --sym none
python ../../mesh/TopLoad.py --amplitude -0.015
ls-dyna-d ncpu=2 i=topcompress.dyn
python ../../post/create_disp_dat.py
python ../../post/create_res_sim_mat.py --dynadeck topcompress.dyn
