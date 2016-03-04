#!/bin/env python
#SBATCH --mem=4G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mail-user=mlp6@duke.edu
#SBATCH --mail-type=END

from time import ctime
from os import environ, system
from socket import gethostname
from fem.mesh import GenMesh, bc
from fem.mesh.GaussExc import generate_loads
from fem.post.create_disp_dat import create_dat as create_disp_dat
from fem.post.create_res_sim_mat import run as create_res_sim_mat

print('STARTED: %s' % ctime())
print('HOST: %s' % gethostname())

DYNADECK='gauss_qsym_pml.dyn'
NTASKS = environ.get('SLURM_NTASKS', '8')

xyz = (-1.5, 0.0, 0.0, 1.5, -3.0, 0.0)
numElem = (75, 75, 150)
GenMesh.run(xyz, numElem)

# setup quarter symmetry condition
pml_elems = ((5, 0), (0, 5), (5, 5))
face_constraints = (('1,1,1,1,1,1', '1,0,0,0,1,1'),
                    ('0,1,0,1,0,1', '1,1,1,1,1,1'),
                    ('1,1,1,1,1,1', '1,1,1,1,1,1'))
edge_constraints = (((0,1),(1,0),(0,0)),'1,1,0,1,1,1')
bc.apply_pml(pml_elems, face_constraints, edge_constraints)

generate_loads([0.25,0.25,0.75], [0.0,0.0,-1.5])

system('ls-dyna-d ncpu=%s i=%s' % (NTASKS, DYNADECK))

create_disp_dat()

create_res_sim_mat('gauss_qsym_pml.dyn')

#if [ -e res_sim.mat ];
#    then rm d3* nodout;
#fi

#xz -v disp.dat

print('FINISHED: %s' % ctime())
