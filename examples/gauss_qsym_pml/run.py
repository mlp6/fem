#!/bin/env python
#SBATCH --mem=2G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
##SBATCH --mail-user=email@address.edu
##SBATCH --mail-type=END

from time import ctime
from os import environ, system
from socket import gethostname
from fem.mesh import GaussExc

print('STARTED: %s' % ctime())
print('HOST: %s' % gethostname())

DYNADECK='gauss_qsym_pml.dyn'
NTASKS = environ.get('SLURM_NTASKS', '8')

import gen_mesh_bc
gen_mesh_bc.main()
loads = GaussExc.read_process_nodes([0.25,0.25,0.75], [0.0,0.0,-1.5],)
GaussExc.write_load_file('loads.dyn', loads)
#system('ls-dyna-d ncpu=%s i=%s' % (NTASKS, DYNADECK))
#system('python %s/post/create_disp_dat.py' % FEMGIT)
#system('python %s/post/create_res_sim_mat.py --dynadeck %s' % (FEMGIT, DYNADECK))

#if [ -e res_sim.mat ];
#    then rm d3* nodout;
#fi

#xz -v disp.dat

print('FINISHED: %s' % ctime())
