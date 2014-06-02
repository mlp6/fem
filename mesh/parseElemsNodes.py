#!/usr/local/bin/python2.7
'''

Copyright 2014 Mark L. Palmeri (mlp6@duke.edu)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

__author__ = "Mark Palmeri"
__date__ = "2010-12-19"
__version__ = "0.1"

import argparse

parser = argparse.ArgumentParser(description="Create node and element definition files from ls-prepost-generated mesh.")
parser.add_argument("--nodefile",dest="nodefile",help="Node definition file [default = nodes.dyn]",default="nodes.dyn")
parser.add_argument("--elefile",dest="elefile",help="Element definition file [default = elems.dyn]",default="elems.dyn")
parser.add_argument("--mesh",dest="mesh",help="Mesh input (from ls-prepost) [default = mesh.dyn]",default="mesh.dyn")

args = parser.parse_args()

NODEFILE = open(args.nodefile,'w')
ELEMFILE = open(args.elefile,'w')

NODEFILE.write('*NODE\n')
ELEMFILE.write('*ELEMENT_SOLID\n')

MESHFILE = open(args.mesh,'r')
ELE = False
NODE = False
for i in MESHFILE:
    if i.startswith('*') and (ELE == True or NODE == True):
        if ELE == True:
            ELE = False
        if NODE == True:
            NODE = False
    if i.startswith('*ELEMENT_SOLID'):
        ELE = True
        continue
    if i.startswith('*NODE'):
        NODE = True
        continue
    if ELE == True or NODE == True:
        if not i.startswith('$'):
            line = i.split()
            if ELE == True:
                ELEMFILE.write(','.join(line) + '\n')
            elif NODE == True:
                # limiting to first 4 entries since lspp appears to be adding some extra numbers in the node entries now
                NODEFILE.write(','.join(line[0:4]) + '\n')

# print to footer for each file
NODEFILE.write('*END\n')
ELEMFILE.write('*END\n')

NODEFILE.close()
ELEMFILE.close()
