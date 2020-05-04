"""green2para.py - convert 4D data from Green's simulations into Paraview format (PVD/VTR)"""
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main(matfile="Zdisp4D.mat", Xmm='Xmm', Ymm='Ymm', Zmm='Zmm', Zdisp='Zdisp', tms='tms'):
    """extract 4D displacement data from Matlab file and write to Paraview PVD/VTR format

    Args:
        matfile: Matlab file
        Xmm: X-axis array
        Ymm: Y-axis array
        Zmm: Z-axis array
        Zdisp: 4D displacement matrix (X x Y x Z x time)
        tms: time array

    Returns:

    """
    from scipy.io import loadmat
    from pyevtk.hl import gridToVTK
    from pathlib import Path

    matdata = Path(matfile)
    datafile_prefix = matdata.with_suffix('')
    data = loadmat(matdata)

    with open(f'{datafile_prefix.name}.pvd', 'w') as pvd:

        pvd.write('<?xml version="1.0"?>\n')
        pvd.write('<VTKFile type="Collection" version="0.1" '
                    'byte_order="LittleEndian" '
                    'compressor="vtkZLibDataCompressor">\n')
        pvd.write('    <Collection>\n')

        for ts, time in enumerate(data[tms].ravel()):

            zdisp = data[Zdisp][:, :, :, ts]

            vtrfilename = Path(f'{datafile_prefix.name}_T{ts:04d}.vtr')

            logger.info(f'Writing file: {vtrfilename}')

            pvd.write(f'        <DataSet timestep="{time}" group="" part="" file="{vtrfilename.name}"/>\n')

            gridToVTK(vtrfilename.with_suffix('').name,
                    data[Xmm].ravel(),
                    data[Ymm].ravel(),
                    data[Zmm].ravel(),
                    pointData={Zdisp: zdisp}
            )
        pvd.write('    </Collection>\n')
        pvd.write('</VTKFile>\n')

if __name__ == "__main__":
    main()
