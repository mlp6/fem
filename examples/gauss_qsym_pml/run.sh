#!/bin/bash
#SBATCH --mem=2G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
##SBATCH --mail-user=email@address.edu
##SBATCH --mail-type=END

date
echo $SLURMD_NODENAME

FEMGIT='/path/to/fem'
DYNADECK='gauss_qsym_pml.dyn'

python ./gen_mesh_bc.py
python $FEMGIT/mesh/GaussExc.py --sigma 0.25 0.25 0.75 --center 0.0 0.0 -1.5
ls-dyna-d ncpu=$SLURM_NTASKS i=$DYNADECK
python $FEMGIT/post/create_disp_dat.py
python $FEMGIT/post/create_res_sim_mat.py --dynadeck $DYNADECK

#if [ -e res_sim.mat ]; 
#    then rm d3* nodout; 
#fi

#xz -v disp.dat

date
