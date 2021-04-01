from os import environ, system
from socket import gethostname
from time import ctime

from fem.mesh import GenMesh, bc
from fem.mesh.GaussExc import generate_loads
from fem.post.create_disp_dat import create_dat as create_disp_dat
from fem.post import create_res_sim

print('STARTED: {}'.format(ctime()))
print('HOST: {}'.format(gethostname()))

##DYNADECK = 'gauss_qsym_pml.dyn'
DYNADECK = 'gauss_qsym_pml.dyn'
NTASKS = environ.get('SLURM_NTASKS', '8')

##GenMesh.run((-2.0, 2.0, -2.0, 2.0, -4.0, 0.0), (160, 160, 160))

# setup no-symmetry condition
##pml_elems = ((5, 5), (5, 5), (5, 5))
##face_constraints = (('1,0,0,0,1,1', '1,0,0,0,1,1'),
##                    ('0,1,0,1,0,1', '0,1,0,1,0,1'),
##                   ('1,1,1,1,1,1', '1,1,1,1,1,1'))
##edge_constraints = (((0, 1), (1, 0), (0, 0)), '1,1,0,1,1,1')
##bc.apply_pml(pml_elems, face_constraints, edge_constraints)

##generate_loads([0.25, 0.25, 0.75], [0.0, 0.0, -1.5])

##system('ls-dyna-d ncpu={} i={}'.format(NTASKS, DYNADECK))
#system('singularity exec -p -B /work/aek27/TestingFemTools2021/TI_attempt4 /opt/apps/staging/ls-dyna-singularity/ls-dyna.sif ls-dyna-d ncpu={} i={} memory=600000000'.format(NTASKS, DYNADECK))



#create_disp_dat()
create_res_sim.run(dynadeck=DYNADECK, 
                   dispout = "disp.dat",
                   ressim= "res_sim_coronal.mat", 
                   plane_pos = 0.0, 
                   plane_orientation = 2)
create_res_sim.run(dynadeck=DYNADECK,
                   dispout = 'disp.dat',
                   ressim = 'res_sim_elev.mat',
                   plane_pos = 0.0, 
                   plane_orientation = 1)
create_res_sim.run(DYNADECK,
                   dispout="disp.dat",
                   ressim="res_sim.mat")
create_res_sim.run(dynadeck=DYNADECK,
                   dispout="disp.dat",
                   ressim='res_sim.h5')
create_res_sim.extract3Darfidata(dynadeck=DYNADECK,
                                 dispout="disp.dat",
                                 ressim="res_sim.pvd")
##create_res_sim.run(dynadeck=DYNADECK,
#                   dispout="disp.dat",
#                   ressim='res_sim.h5')
##create_res_sim.extract3Darfidata(dynadeck=DYNADECK,
 #                                dispout="disp.dat",
 #                                ressim="res_sim.pvd")

##os.system("xz -v disp.dat")

print('FINISHED: {}'.format(ctime()))

