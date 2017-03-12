def test_preallocate_arfidata():
    from fem.post.create_res_sim_mat import preallocate_arfidata
    arfidata = preallocate_arfidata(image_plane)

    pass

def test_extract_image_plane(sorted_nodes, axes):
    from fem.post.create_res_sim_mat import extract_image_plane

    image_plane = extract_image_plane(sorted_nodes, axes, 0.0)

    assert image_plane.shape == (11, 11)
    assert image_plane[0][0] == 11
    assert image_plane[0][-1] == 1221
    assert image_plane[-1][0] == 121
    assert image_plane[-1][-1] == 1331
