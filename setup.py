from distutils.core import setup
import sys

if sys.version_info.major != 3 or (sys.version_info.major == 3 and
                                   sys.version_info.minor < 6):
    sys.exit('You must use python >=3.6')

setup(
    name='Acoustic Radiation Force FEM Tools',
    version='6.6.1',
    packages=['fem', ],
    license='Apache v2.0',
    author='Mark Palmeri',
    author_email='mlp6@duke.edu',
    long_description=open('README.md').read(),
    url='https://github.com/mlp6/fem'
)
