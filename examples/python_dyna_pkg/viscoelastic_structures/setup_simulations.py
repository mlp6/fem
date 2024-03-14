# Sets up 8 total simulations (2 struct shapes, 2 inclusion materials, 2 background materials = 2*2*2 = 8 simulations)

from itertools import product
import os
import pathlib

from fem.dyna.mesh import UniformCoordinates, UniformMesh
from fem.dyna._structure import Structure
from fem.dyna.material import KelvinMaxwellViscoelastic

# Get index for simulation
SLURM_ARRAY_TASK_ID = int(os.environ["SLURM_ARRAY_TASK_ID"])

# Setup paths and make sure they are pathlib objects
paths = dict(
    field_loads="/proj/gallippilab/projects/batch_load_simulations/loads",
    dyna_sims=pathlib.Path(__file__).parent.resolve(),  # path of current file
)
paths = {k: pathlib.Path(v) for k, v in paths.items()}

# Imaging configuration
txer = "9l4"
att = 0.5
fnum = 1.5
fd = 30

# VisR load configuration
load_curve_id = 1
normalization_isppa = 2000
t_arf = 70e-6
dt = 1e-6
n_arf = 2
tracks_between = 6
prf = 10e3
multipush_params_list = [t_arf, dt, n_arf, tracks_between, prf]

# Inclusion materials
inc_material_list = [
    KelvinMaxwellViscoelastic(density=1, E=13 * 1e3, nu=0.499, eta=0.01),
    KelvinMaxwellViscoelastic(density=1, E=26 * 1e3, nu=0.499, eta=0.01),
]

# Create spherical and cylindrical structures with each inclusion material
struct_list = []
for mat in inc_material_list:
    struct_list.append(
        Structure(
            shape="sphere",
            args=[0, 0, -3, 0.5],
            material=mat,
        )
    )
    struct_list.append(
        Structure(
            shape="cylinder",
            args=[0, -3, 6.49 * 0.5],
            material=mat,
        )
    )

# Background materials
back_material_list = [
    KelvinMaxwellViscoelastic(density=1, E=13 * 1e3, nu=0.499, eta=0.01),
    KelvinMaxwellViscoelastic(density=1, E=13 * 1e3, nu=0.499, eta=2.00),
]

# Loop over every combination of parameters
params = list(product(struct_list, back_material_list))
struct, material = params[SLURM_ARRAY_TASK_ID]

# Create mesh
coords = UniformCoordinates(
    grid_size=150,  # microns
    xmin=-1.0,
    xmax=0.0,  # ele
    ymin=0.0,
    ymax=1.0,  # lat
    zmin=-4.0,
    zmax=0.0,  # ax
)
symmetry = "q"
mesh = UniformMesh(coords, symmetry, material)

# Add structure to mesh
mesh.add_struct_list([struct])

# Add pml to mesh
mesh.add_pml(pml_thickness=7, exclude_faces=["zmax"])

# Constrain boundary nodes (do this after adding structures and PML)
mesh.constrain_boundary_nodes()

# Set total simulation time and time step to save results
mesh.set_control(end_time=8e-3)
mesh.set_database(dt=0.5e-4)

# Add load to mesh from pregenerated field loads
if fd < 25:
    load_name = f"txer=l94_row1,fd=[0,0,{fd}],fnum={fnum},att={att}"
else:
    load_name = f"txer=l94_row3,fd=[0,0,{fd}],fnum={fnum},att={att}"

field_load_file = paths["field_loads"] / f"{load_name}.mat"
mesh.add_load_curve(load_curve_id, "multipush", multipush_params_list)
mesh.add_field_arf_load(field_load_file, normalization_isppa, load_curve_id)

# Write dyna cards and create simulation folder structure
sims_path = paths["dyna_sims"] / f"inc_shape={struct.shape}"
material_folder_name = f"inc_e={struct.material.E/1e3:.0f},v={struct.material.eta}_back_e={material.E/1e3:.0f},v={material.eta}"
load_folder_name = load_name
mesh.write_all_dyna_cards(sims_path, load_folder_name, material_folder_name)
