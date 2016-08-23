def extract3Darfidata(dynadeck, disp_comp=2, disp_scale=-1e4, ressim="res_sim.mat", nodedyn="nodes.dyn", dispout="disp.dat.xz"):

    from fem.mesh import fem_mesh
    import fem.post.create_res_sim_mat as crsm
    import numpy as np

    node_id_coords = fem_mesh.load_nodeIDs_coords(nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)

    header = crsm.read_header(dispout)
    dt = crsm.extract_dt(dynadeck)
    t = [float(x) * dt for x in range(0, header['num_timesteps'])]

    arfidata = crsm.extract_arfi_data(dispout, header, snic['id'], disp_comp,
                                      disp_scale, legacynodes=False)

    crsm.save_res_mat(ressim, arfidata, axes, t)

