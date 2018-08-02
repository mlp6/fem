from setuptools import setup
import sys

if sys.version_info.major != 3 or (sys.version_info.major == 3 and
                                   sys.version_info.minor < 4):
    sys.exit('You must use python >=3.4')

setup(
    name='fem',
    packages=['fem', 'fem.mesh', 'fem.post', 'fem.field'],
    package_dir={'fem': '.'},
    version='7.3.2',
    license='Apache v2.0',
    author='Mark Palmeri',
    author_email='mlp6@duke.edu',
    description='FEM',
    keywords=['arfi', 'swei', 'fem', 'ultrasound'],
    long_description=open('README.md').read(),
    url='https://github.com/mlp6/fem',
    download_url='https://github.com/mlp6/fem/archive/v7.3.2.tar.gz',
    classifiers=[],
    install_requires=['h5py', 'ipython', 'jupyter', 'matplotlib', 'numpy',
                      'pytest', 'pytest-pep8', 'scipy', 'sphinx',
                      'sphinxcontrib-napoleon', 'pyevtk'],
    package_data={'fem': ['*.md', 'examples/*/*', 'docs/*']},
    include_package_data=True,
)
