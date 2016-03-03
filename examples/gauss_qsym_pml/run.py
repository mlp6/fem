#!/bin/env python
#SBATCH --mem=2G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
##SBATCH --mail-user=email@address.edu
##SBATCH --mail-type=END

from time import ctime
from os import environ, system
from socket import gethostname

print('STARTED: %s' % ctime())
print('HOST: %s' % gethostname())

FEMGIT='/home/mlp6/projects/fem'
DYNADECK='gauss_qsym_pml.dyn'
NTASKS = environ.get('SLURM_NTASKS', '8')

system('python ./gen_mesh_bc.py')
system('python %s/mesh/GaussExc.py --sigma 0.25 0.25 0.75 --center 0.0 0.0 -1.5' % FEMGIT)
system('ln -s gauss_exc_sigma_0.250_0.250_0.750_center_0.000_0.000_-1.500_amp_1.000_amp_cut_0.050_qsym.dyn loads.dyn')
system('ls-dyna-d ncpu=%s i=%s' % (NTASKS, DYNADECK))
system('python %s/post/create_disp_dat.py' % FEMGIT)
system('python %s/post/create_res_sim_mat.py --dynadeck %s' % (FEMGIT, DYNADECK))

#if [ -e res_sim.mat ];
#    then rm d3* nodout;
#fi

#xz -v disp.dat

print('FINISHED: %s' % ctime())
