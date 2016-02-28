python ../../mesh/GaussExc.py --sigma 0.25 0.25 0.75 --center 0.0 0.0 -1.5 
ls-dyna-s ncpu=2 i=gauss_pml.dyn
rm d3* 
python ../../post/create_disp_dat.py --dat --vtk
python ../../post/create_res_sim_mat.py --dynadeck gauss_pml.dyn
