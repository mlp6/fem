import sys
sys.path.append("../mesh")

import GenMesh as mesh

numElem = (10, 10, 10)
pos = mesh.calc_node_pos((-1.0, 0.0, 0.0, 1.0, -1.0, 0.0), numElem)
mesh.writeNodes(pos)
mesh.writeElems(numElem)
