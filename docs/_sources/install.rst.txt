Installation
============

- All of the Python scripts require Python >= 3.4; 3.6.x is recommended.

- If you just plan to use (not develop) this code, then you can use pip to
  install this in a local virtualenv (make sure it is activated before you run
  this command!): ``pip install git+https://github.com/mlp6/fem.git``

- You can also locally clone this repository: ``git clone
  https://github.com:mlp6/fem.git``.  You will need to properly define
  ``PYTHONPATH`` in your environment to include the root directory that the fem
  repository was cloned into.

- If you locally clone the repository, there is a pip ``requirements.txt`` file
  available to setup a python virtual environment will all of the necessary
  packages (`pip install -r requirements.txt`).
  
- Most code can be utilized as importable modules as part of the fem package,
  or can be executed from the CLI.  Most CLI-executed scripts have help
  available using the ``--help`` flag.

