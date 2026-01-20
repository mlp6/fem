# CLAUDE.md

This file provides guidance for Claude Code when working with this repository.

## Project Overview

FEM is a Python toolkit for simulating acoustic radiation force excitations and shear wave propagation in soft tissue using finite element methods. It integrates with LS-DYNA, a commercial finite element solver.

## Build and Test Commands

```bash
# Install package in development mode
pip install -e .

# Run tests (uses pytest with parallel execution)
pytest -v tests/

# Build documentation
cd docs && make html
```

## Project Structure

```
fem/
├── mesh/       # Mesh generation and boundary conditions
├── dyna/       # LS-DYNA mesh/material definitions (v9.0.0+ dataclass-based)
├── post/       # Post-processing LS-DYNA output to HDF5/MAT/VTK
├── field/      # Field II acoustic simulation integration
tests/          # Pytest tests with fixture data (nodes.dyn, elems.dyn, nodout)
examples/       # Complete workflow examples
docs/           # Sphinx RST documentation
```

## Key Conventions

### Coordinate System (LS-DYNA)
- Axial: -z direction
- Lateral: +y direction
- Elevation: -x direction
- Units: CGS (centimeters, grams, seconds)

### Data Structures
- Node arrays: `[id, x, y, z, tc, rc]` as numpy structured arrays
- Element arrays: `[id, pid, n1-n8]` for 8-node solid elements
- Common naming: `nodeIDcoords` (nic), `sortedNodeIDcoords` (snic)
- Spatial sorting uses Fortran order ('F') for LS-DYNA compatibility

### File Formats
- `.dyn` - LS-DYNA keyword input files (comma-separated, `*` or `$` prefix for comments)
- `nodout` - LS-DYNA binary node output
- Output formats: HDF5 (.h5), MAT (v5), VTR/PVD (Paraview)

### Architecture Patterns (v9.0.0+)
- Dataclass-based design with `@dataclass` decorator
- Mixin pattern in `fem/dyna/`: `_structure.py`, `_constraints.py`, `_loads.py`, `_writer.py`
- Material hierarchy with base `Material` class

## Dependencies

Core: numpy, scipy, h5py, matplotlib, pyevtk
Build: scikit-build, cmake (for C/SWIG acceleration in post-processing)
Docs: sphinx>=7.2.0

## Common Workflows

1. Generate mesh: `GenMesh.run(xyz_bounds, num_elements)`
2. Apply boundary conditions: `bc.apply_face_bc_only(face_constraints)`
3. Define loads: `TopLoad.generate_loads(loadtype='disp', ...)`
4. Run LS-DYNA (external)
5. Extract results: `create_disp_dat()` (nodout → HDF5)
6. Generate visualization: `create_res_sim()` (HDF5/MAT/PVD)

## CI/CD

- GitHub Actions workflows in `.github/workflows/`
- `python-package.yml` - Runs pytest on Python 3.11
- `docs.yml` - Builds and deploys Sphinx docs to GitHub Pages
