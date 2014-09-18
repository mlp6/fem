python ../mesh/GenMesh.py --xyz -0.5 0.0 0.0 1.0 -3.0 0.0 --numElem 10 20 60
python ../mesh/bc.py
python ../mesh/GaussExc.py --sigma 0.25 0.25 0.75 --center 0.0 0.0 -1.5 
matlab -nodesktop -nosplash -r "addpath('/home/mlp6/git/fem/field'); field2dyna('nodes.dyn',0.5,1.0,[0.0 0.0 0.02],7.2,'vf105','gaussian')"
