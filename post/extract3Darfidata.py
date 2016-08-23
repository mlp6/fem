def extract3Darfidata(dynadeck, disp_comp=2, disp_scale=-1e4, ressim="res_sim.mat", nodedyn="nodes.dyn", dispout="disp.dat.xz"):

    from fem.mesh import fem_mesh
    import fem.post.create_res_sim_mat as crsm
    from scipy.io import savemat
    import numpy as np

    node_id_coords = fem_mesh.load_nodeIDs_coords(nodedyn)
    [snic, axes] = fem_mesh.SortNodeIDs(node_id_coords)

    header = crsm.read_header(dispout)
    dt = crsm.extract_dt(dynadeck)
    t = [float(x) * dt for x in range(0, header['num_timesteps'])]

    arfidata = np.empty([len(axes[2]), len(axes[1]), len(t), len(axes[0])])
    for i, e in enumerate(axes[0]):
        image_plane = crsm.extract_image_plane(snic, axes, ele_pos=e)
        arfidata[:, :, :, i] = crsm.extract_arfi_data(dispout, header, image_plane, disp_comp, disp_scale, legacynodes=False)

    axial = -10*axes[2]
    savemat(ressim,
            {'arfidata': arfidata,
             'lat': 10*axes[1],
             'axial': axial[::-1],
             'elev': -axes[0],
             't': t},
            do_compression=True
            )

