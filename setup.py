from setuptools import setup

setup(
    name='fem',
    packages=['fem', 'fem.mesh', 'fem.post', 'fem.field'],
    package_dir={'fem': 'fem'},
    version='7.3.4',
    license='Apache v2.0',
    author='Mark Palmeri',
    author_email='mlp6@duke.edu',
    description='FEM',
    keywords=['arfi', 'swei', 'fem', 'ultrasound'],
    long_description=open('README.md').read(),
    url='https://github.com/mlp6/fem',
    download_url='https://github.com/mlp6/fem/archive/v7.3.4.tar.gz',
    classifiers=[],
    install_requires=['h5py', 'ipython', 'jupyter', 'matplotlib', 'numpy>=1.16',
                      'pytest', 'pytest-pep8', 'scipy', 'sphinx',
                      'sphinxcontrib-napoleon', 'pyevtk', 'pyyaml'],
    python_requires=">3.7",
    package_data={'fem': ['*.md', 'examples/*/*', 'docs/*']},
    include_package_data=True,
)
