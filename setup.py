from distutils.core import setup
import sys

if sys.version_info.major != 3 or (sys.version_info.major == 3 and
                                   sys.version_info.minor < 6):
    sys.exit('You must use python >=3.6')

setup(
    name='arfi_fem',
    packages=['arfi_fem', ],
    version='6.8.2',
    license='Apache v2.0',
    author='Mark Palmeri',
    author_email='mlp6@duke.edu',
    description='Acoustic Radiation Force FEM Tools',
    keywords=['arfi', 'swei', 'fem'],
    long_description=open('README.md').read(),
    url='https://github.com/mlp6/fem',
    download_url='https://github.com/mlp6/fem/archive/v6.8.2.tar.gz',
    classifiers=[],
)
