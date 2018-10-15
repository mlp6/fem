#!/bin/env python
#SBATCH --mem=4G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
##SBATCH --mail-user=netid@duke.edu
##SBATCH --mail-type=END

import os
from os import environ, system
from socket import gethostname
from time import ctime

from fem.mesh import GenMesh, bc
from fem.mesh.GaussExc import generate_loads
from fem.post.create_disp_dat import create_dat as create_disp_dat
from fem.post.create_res_sim import run as create_res_sim

print('STARTED: {}'.format(ctime()))
print('HOST: {}'.format(gethostname()))

DYNADECK = 'tukey_gauss_qsym_pml.dyn'
NTASKS = environ.get('SLURM_NTASKS', '8')

GenMesh.run((-1.5, 0.0, 0.0, 1.5, -3.0, 0.0), (75, 75, 150))

# setup quarter-symmetry condition
pml_elems = ((5, 0), (0, 5), (5, 5))
face_constraints = (('1,1,1,1,1,1', '1,0,0,0,1,1'),
                    ('0,1,0,1,0,1', '1,1,1,1,1,1'),
                    ('1,1,1,1,1,1', '1,1,1,1,1,1'))
edge_constraints = (((0, 1), (1, 0), (0, 0)), '1,1,0,1,1,1')
bc.apply_pml(pml_elems, face_constraints, edge_constraints)

generate_loads([0.1, 0.1, 0.75], [0.0, 0.0, -1.5], tukey_length=2.5)

system('ls-dyna-d ncpu={} i={}'.format(NTASKS, DYNADECK))

create_disp_dat()

create_res_sim(DYNADECK)

if os.path.exists('res_sim.mat'):
    os.system("rm d3* nodout")
    os.system("xz -v disp.dat")

print('FINISHED: {}'.format(ctime()))
