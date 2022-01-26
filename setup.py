from setuptools import setup, Extension

setup(
    name='fem',
    packages=['fem', 'fem.mesh', 'fem.post', 'fem.field'],
    package_dir={'fem': 'fem'},
    version='8.5.0',
    license='Apache v2.0',
    author='Mark Palmeri',
    author_email='mlp6@duke.edu',
    description='FEM',
    keywords=['arfi', 'swei', 'fem', 'ultrasound'],
    long_description=open('README.md').read(),
    url='https://github.com/mlp6/fem',
    download_url='https://github.com/mlp6/fem/archive/refs/tags/v8.5.0.zip',
    classifiers=[],
    install_requires=['h5py',
                      'numpy>=1.16',
                      'scipy',
                      'matplotlib',
                      'pyevtk', ],
    python_requires=">=3.8",
    package_data={'fem': ['*.md', 'examples/*/*', 'docs/*']},
    include_package_data=True,
    zip_safe=False,
    ext_modules=[Extension(name='fem/post/_create_disp_dat_fast',
                           sources=["fem/post/create_disp_dat_fast.i",
                                    "fem/post/create_disp_dat_fast.c"])]
)
