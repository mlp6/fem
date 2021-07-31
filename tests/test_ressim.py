from pathlib import Path

examplesPath = Path(__file__).parents[1] / "examples"
gauss_qsym_pml_example_path = examplesPath / "gauss_qsym_pml"


def test_ressim_load_mat(tmpdir):
    from fem.post.ressim import ResSim

    resmat = ResSim(filename=f"{gauss_qsym_pml_example_path}/res_sim_valid.h5")

    assert isinstance(resmat, ResSim)


def test_ressim_load_hdf5(tmpdir):
    from fem.post.ressim import ResSim

    resh5 = ResSim(filename=f"{gauss_qsym_pml_example_path}/res_sim_valid.h5")

    assert isinstance(resh5, ResSim)
