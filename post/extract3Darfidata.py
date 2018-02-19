def extract3Darfidata(dynadeck, disp_comp=2, disp_scale=-1e4,
                      ressim="res_sim.h5", nodedyn="nodes.dyn",
                      dispout="disp.dat.xz"):
    """extract 3D volume of specified displacement component

    :param dynadeck: LS-DYNA3D input deck (used to get dt)
    :param disp_comp=2: displacement component to extract (0, 1, 2)
    :param disp_scale=1e4: displacement scaling factor (cm -> um)
    :param ressim="res_sim.h5": output file name (can be MAT or HDF5)
    :param nodedyn="nodes.dyn": node input file
    :param dispout="disp.dat.xz": binary displacement data
    """

    from fem.mesh import fem_mesh
    import fem.post.create_res_sim_mat as create_res_sim
    import numpy as np

    node_id_coords = fem_mesh.load_nodeIDs_coords(nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)

    header = create_res_sim.read_header(dispout)
    dt = create_res_sim.extract_dt(dynadeck)
    t = [float(x) * dt for x in range(0, header['num_timesteps'])]

    arfidata = create_res_sim.extract_arfi_data(dispout, header, snic['id'],
                                                disp_comp, disp_scale,
                                                legacynodes=False)

    create_res_sim.save_res_mat(ressim, arfidata, axes, t)
