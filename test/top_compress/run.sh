python ../mesh/GenMesh.py --xyz -0.5 0.0 0.0 1.0 -3.0 0.0 --numElem 10 20 60
python ../mesh/bc.py --notop --sym none
python ../mesh/TopLoad.py --amplitude -0.015
