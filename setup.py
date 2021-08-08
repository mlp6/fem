from skbuild import setup


setup(
    name='fem',
    packages=['fem', 'fem.mesh', 'fem.post', 'fem.field'],
    package_dir={'fem': 'fem'},
    version='8.3.1',
    license='Apache v2.0',
    author='Mark Palmeri',
    author_email='mlp6@duke.edu',
    description='FEM',
    keywords=['arfi', 'swei', 'fem', 'ultrasound'],
    long_description=open('README.md').read(),
    url='https://github.com/mlp6/fem',
    download_url='https://github.com/mlp6/fem/archive/refs/tags/v8.3.1.zip',
    classifiers=[],
    install_requires=['h5py',
                      'numpy>=1.16',
                      'scipy',
                      'matplotlib',
                      'pyevtk', ],
    python_requires=">=3.8",
    package_data={'fem': ['*.md', 'examples/*/*', 'docs/*']},
    include_package_data=True,
    cmake_source_dir='fem/post',
    cmake_install_dir='fem/post',
)
