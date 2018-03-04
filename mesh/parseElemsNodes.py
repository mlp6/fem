"""
Copyright 2015 Mark L. Palmeri (mlp6@duke.edu)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__author__ = "Mark Palmeri"
__date__ = "2010-12-19"
__version__ = "0.1"


def main():
    """ """
    import argparse as ap

    # TODO: move argparse to own function
    p = ap.ArgumentParser(description="Create node and element definition"
                                      "files from lspp4-generated mesh.")
    p.add_argument("--nodefile",
                   dest="nodefile",
                   help="Node definition file [default = nodes.dyn]",
                   default="nodes.dyn")
    p.add_argument("--elefile",
                   dest="elefile",
                   help="Element definition file [default = elems.dyn]",
                   default="elems.dyn")
    p.add_argument("--mesh",
                   dest="mesh",
                   help="Mesh input (from ls-prepost) [default = mesh.dyn]",
                   default="mesh.dyn")

    args = p.parse_args()

    with open(args.nodefile, 'w') as NODEFILE:
        with open(args.elefile, 'w') as ELEMFILE:

            NODEFILE.write('*NODE\n')
            ELEMFILE.write('*ELEMENT_SOLID\n')

            ELE = False
            NODE = False
            with open(args.mesh, 'r') as MESHFILE:

                for i in MESHFILE:
                    if i.startswith('*') and (ELE is True or NODE is True):
                        if ELE is True:
                            ELE = False
                        if NODE is True:
                            NODE = False
                    if i.startswith('*ELEMENT_SOLID'):
                        ELE = True
                        continue
                    if i.startswith('*NODE'):
                        NODE = True
                        continue
                    if ELE is True or NODE is True:
                        if not i.startswith('$'):
                            line = i.split()
                            if ELE is True:
                                ELEMFILE.write(','.join(line) + '\n')
                            elif NODE is True:
                                # limit to first 4 entries since lspp appears
                                # to be adding extra numbers
                                NODEFILE.write(','.join(line[0:4]) + '\n')

            # print to footer for each file
            NODEFILE.write('*END\n')
            ELEMFILE.write('*END\n')


if __name__ == "__main__":
    main()
