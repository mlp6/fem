#!/bin/env python
#SBATCH --mem=2G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
##SBATCH --mail-user=email@address.edu
##SBATCH --mail-type=END

from time import ctime
from os import environ, system
from socket import gethostname
import gen_mesh_bc
from fem.mesh import GaussExc
from fem.post.create_disp_dat import create_dat as create_disp_dat
from fem.post.create_res_sim_mat import run as create_res_sim_mat

print('STARTED: %s' % ctime())
print('HOST: %s' % gethostname())

DYNADECK='gauss_qsym_pml.dyn'
NTASKS = environ.get('SLURM_NTASKS', '8')

gen_mesh_bc.main()
loads = GaussExc.read_process_nodes([0.25,0.25,0.75], [0.0,0.0,-1.5],)
GaussExc.write_load_file('loads.dyn', loads)
system('ls-dyna-d ncpu=%s i=%s' % (NTASKS, DYNADECK))
create_disp_dat()
create_res_sim_mat()

#if [ -e res_sim.mat ];
#    then rm d3* nodout;
#fi

#xz -v disp.dat

print('FINISHED: %s' % ctime())
