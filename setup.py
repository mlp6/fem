from setuptools import setup
import sys
import __version__

if sys.version_info.major != 3 or (sys.version_info.major == 3 and
                                   sys.version_info.minor < 5):
    sys.exit('You must use python >=3.5')

setup(
    name='fem',
    packages=['fem', 'fem.mesh', 'fem.post'],
    package_dir={'fem': '.'},
    version='6.9.1',
    license='Apache v2.0',
    author='Mark Palmeri',
    author_email='mlp6@duke.edu',
    description='FEM',
    keywords=['arfi', 'swei', 'fem'],
    long_description=open('README.md').read(),
    url='https://github.com/mlp6/fem',
    download_url='https://github.com/mlp6/fem/archive/v6.9.1.tar.gz',
    classifiers=[],
)
