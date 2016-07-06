Installation
============

- You can locally clone this repository:
   ``git clone git@gitlab.oit.duke.edu:mlp6/fem.git``

This approach will work if you have an `SSH
key <https://help.github.com/articles/generating-ssh-keys>`__ uploaded
to GitLab. If not, then you can also clone the reportory using:
``git clone https://gitlab.oit.duke.edu/mlp6/fem.git``

- Add the fem subdirectories to your Matlab path. One approach is to add the
  following to ``$HOME/matlab/startup.m``: ``fem_root =
  'PATH/TO/GIT/CLONED/fem';  addpath(fullfile(fem_root, 'mesh'));
  addpath(fullfile(fem_root, 'field'));  addpath(fullfile(fem_root, 'post'));``
  where ``fem_root`` is the path of your git-cloned fem repository.

- Siemens proprietary probe definitions can be cloned from the Duke
  access-restricted repository: https://gitlab.oit.duke.edu/ultrasound/probes .

- All of the python scripts require python >=3.3.  
  
- Most code can be utilized as importable modules as part of the fem package,
  or can be executed from the CLI.  Most CLI-executed scripts have help
  available using the ``--help`` flag.

- If you are importing the fem code as a python package, then be sure to
  properly define ``PYTHONPATH`` in your environment to include the root
  directory that the fem repository was cloned into.

- There is a pip ``requirements.txt`` file available to setup a python virtual
  environment will all of the necessary packages.
