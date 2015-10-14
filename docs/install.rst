Installation
============

-  You can locally clone this repository:
   ``git clone git@gitlab.oit.duke.edu:mlp6/fem.git``

This approach will work if you have an `SSH
key <https://help.github.com/articles/generating-ssh-keys>`__ uploaded
to GitHub. If not, then you can also clone the reportory using:
``git clone http://gitlab.oit.duke.edu/mlp6/fem.git``

-  Add the fem subdirectories to your Matlab path. One approach is to
   add the following to ``$HOME/matlab/startup.m``:
   ``fem_root = 'PATH/TO/GIT/CLONED/fem';  addpath(fullfile(fem_root, 'mesh'));  addpath(fullfile(fem_root, 'field'));  addpath(fullfile(fem_root, 'post'));``
   where ``fem_root`` is the path of your git-cloned fem repository.

-  Siemens proprietary probe definitions can be cloned from the Duke
   access-restricted repository:
   https://gitlab.oit.duke.edu/ultrasound/probes .

-  All of the python scripts require python >=2.7 and are python3
   compliant. All scripts have help available using the ``--help`` flag.
