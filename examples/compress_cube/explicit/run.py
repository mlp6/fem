#!/bin/env python
#SBATCH --mem=4G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
##SBATCH --mail-user=netid@duke.edu
##SBATCH --mail-type=END

from os import environ, system
from socket import gethostname
from time import ctime

from fem.mesh import GenMesh, bc
from fem.mesh.TopLoad import generate_loads
from fem.post.create_disp_dat import create_dat as create_disp_dat
from fem.post.create_res_sim_mat import run as create_res_sim_mat

print('STARTED: %s' % ctime())
print('HOST: %s' % gethostname())

DYNADECK='CompressElasticCubeExplicit.dyn'
NTASKS = environ.get('SLURM_NTASKS', '8')

xyz = (-1.0, 0.0, 0.0, 1.0, -1.1, -0.1)
numElem = (10, 10, 10)
GenMesh.run(xyz, numElem)

# restrict penetration of the zmin face
face_constraints = (('0,0,0,0,0,0', '0,0,0,0,0,0'),
                    ('0,0,0,0,0,0', '0,0,0,0,0,0'),
                    ('0,0,1,1,1,0', '0,0,0,0,0,0'))
bc.apply_face_bc_only(face_constraints)

# apply displacement condition to the zmax face
generate_loads(loadtype='disp', direction=2, amplitude=-0.1,
               top_face=(0, 0, 0, 0, 0, 1), lcid=1)

system('ls-dyna-d ncpu=%s i=%s' % (NTASKS, DYNADECK))

create_disp_dat()

create_res_sim_mat(DYNADECK)

#if os.path.exists('res_sim.mat'):
#    os.system("rm d3* nodout")
#    os.system("xz -v disp.dat")

print('FINISHED: %s' % ctime())
