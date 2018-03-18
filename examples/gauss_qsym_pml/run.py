#!/bin/env python
#SBATCH --mem=4G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --partition=ultrasound
##SBATCH --mail-user=netid@duke.edu
##SBATCH --mail-type=END

from os import environ, system
from socket import gethostname
from time import ctime

from fem.mesh import GenMesh, bc
from fem.mesh.GaussExc import generate_loads
from fem.post.create_disp_dat import create_dat as create_disp_dat
from fem.post import create_res_sim

print('STARTED: {}'.format(ctime()))
print('HOST: {}'.format(gethostname()))

DYNADECK = 'gauss_qsym_pml.dyn'
NTASKS = environ.get('SLURM_NTASKS', '8')

GenMesh.run((-1.5, 0.0, 0.0, 1.5, -3.0, 0.0), (75, 75, 150))

# setup quarter-symmetry condition
pml_elems = ((5, 0), (0, 5), (5, 5))
face_constraints = (('1,1,1,1,1,1', '1,0,0,0,1,1'),
                    ('0,1,0,1,0,1', '1,1,1,1,1,1'),
                    ('1,1,1,1,1,1', '1,1,1,1,1,1'))
edge_constraints = (((0, 1), (1, 0), (0, 0)), '1,1,0,1,1,1')
bc.apply_pml(pml_elems, face_constraints, edge_constraints)

generate_loads([0.25, 0.25, 0.75], [0.0, 0.0, -1.5])

system('ls-dyna-d ncpu={} i={}'.format(NTASKS, DYNADECK))

create_disp_dat()

create_res_sim.run(DYNADECK,
                   dispout="disp.dat",
                   ressim="res_sim.mat")
create_res_sim.run(dynadeck=DYNADECK,
                   dispout="disp.dat",
                   ressim='res_sim.h5')
create_res_sim.extract3Darfidata(dynadeck=DYNADECK,
                                 dispout="disp.dat",
                                 ressim="res_sim.pvd")

os.system("xz -v disp.dat")

print('FINISHED: {}'.format(ctime()))
