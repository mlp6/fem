'''
bc.py - apply boundary conditions to rectangular solid meshes (the majority of the FE sims); can handle quarter- and half-symmetry models.

This code was based on the older BoundCond.pl, but it should (1) be more flexbible, (2) utilizies more command-line options, and (3) allows for segment definition for the non-reflecting bc.

MODIFIED v0.2 (2012-07-02)
* able to accomodate no symmetry in the model (previously was 1/4 or 1/2 symmetry)

MODIFIED v0.3 (2012-12-03)
* updated optparse -> argparse (not python 2.7 required)
* bottom boudary condition can be explicitely set on the commandline, and can be set for in-plane constraint in addition to fully-constrained

MODIFIED v0.4 (2012-12-06)
* MAJOR CHANGE: FE coordinates for dyna are now assume to be the same as Field II (no negative z, nor negative x, and x = lateral, y = elevation, z = depth)
* Added option to explicitely turn on / off non-reflecting face definitions
'''

__author__ = "Mark Palmeri"
__email__ = "mlp6@duke.edu"
__date__ = "2012-07-02"
__revised__ = "2012-12-06"
__version__ = "0.4"


def main():
    import pdb 
    import os,sys,math
    import numpy as n

    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate boundary condition data as specified on the command line.  The center of the transducer is assumed to be at (0,0,0), with lateral = x, elevation = y, depth = z (Field II coordinates).  Face BC options are strings; valid options include: fixed, inplane, free, or sym.  \n\n%prog [OPTIONS]...",version="%s" % __version__)
    parser.add_argument("--bcfile",help="boundary condition output file [default = bc.dyn]",default="bc.dyn")
    parser.add_argument("--nodefile",help="node defintion input file [default = nodes.dyn]",default="nodes.dyn")
    parser.add_argument("--xmin",help="lateral face [default = sym]",default="sym")
    parser.add_argument("--xmax",help="lateral face [default = free]",default="free")
    parser.add_argument("--ymin",help="elevation face [default = sym]",default="sym")
    parser.add_argument("--ymax",help="elevation face [default = free]",default="free")
    parser.add_argument("--zmin",help="constrain transducer face [default = fixed]",default="fixed")
    parser.add_argument("--zmax",help="constrain distal face (opposite transducer face) [default = fixed]",default="fixed")
    parser.add_argument("--noreflect",help="turn on non-reflecting definitions for non-symmetry faces (Boolean default = True)",default="True")

    opts = parser.parse_args()

    # open the boundary condition file to write
    BCFILE = open(opts.bcfile,'w')
    BCFILE.write("$ Generated using %s (version %s) with the following options:\n" % (sys.argv[0],__version__))
    BCFILE.write("$ %s\n" % opts)
    
    # load in all of the node data, excluding '*' lines
    nodeIDcoords = n.loadtxt(opts.nodefile, delimiter=',', comments='*', dtype=[('id','i4'),('x','f4'),('y','f4'),('z','f4')])

    # there are 6 faces in these models; we need to (1) find all of them and (2) apply the appropriate BCs
    # we'll loop through all of the nodes, see if they are on a face or edge, and then apply the appropriate BC
    [snic, axes] = SortNodeIDs(nodeIDcoords)
    
    # create list of the bc user/default options
    bc_face_options = assemble_bc_face_options(opts,axes)

    pdb.set_trace()
    '''
    # initialize segID 
    segID = 1

    # APPLY ZMIN BC
    segID = writeSeg(BCFILE,'ZMAX_FACE',segID,planeNodeIDs)
    
    

    # APPLY ZMAX BC

    # APPLY XMIN BC

    # APPLY XMAX BC

    # APPLY YMIN BC

    # APPLY YMAX BC






    for r in range(0,3):
        for m in ('bcmin','bcmax'):
            if m == 'bcmin':
                plane = (r,axes[r].min())
            elif m == 'bcmax':
                plane = (r,axes[r].max())
            planeNodeIDs = extractPlane(snic,axes,plane)

            if r == 0: # front/back (front - symmetry, back - non-reflecting)
                if m == 'bcmax': # back (non-reflecting)
                    segID = writeSeg(BCFILE,'YMAX',segID,planeNodeIDs)
                elif m == 'bcmin': # front (symmetry)
                    if (opts.sym == 'q') or (opts.sym == 'h'):
                        writeNodeBC(BCFILE,planeNodeIDs[1:-1],'1,0,0,0,1,1') # no zmin / zmax rows (those will be defined in the zmin/zmax defs)
                    else:
                        if opts.sym != 'none':
                            sys.exit("ERROR: invalid symmetry flag specified (front face)")
                        segID = writeSeg(BCFILE,'YMIN_FACE',segID,planeNodeIDs)

            elif r == 1: # left/right (non-reflecting; left - symmetry)
                if m == 'bcmin': # left (push side)
                    # if quarter-symmetry, then apply BCs, in addition to a modified edge; and don't deal w/ zmin/zmax
                    if opts.sym == 'q':
                        writeNodeBC(BCFILE,planeNodeIDs[1:-1],'0,1,0,1,0,1')
                    # else make it a non-reflecting boundary
                    else:
                        if (opts.sym != 'h') and (opts.sym != 'none'):
                            sys.exit("ERROR: invalid symmetry flag specified (left/push face)")
                        segID = writeSeg(BCFILE,'XMIN_FACE',segID,planeNodeIDs) 
                if m == 'bcmax': # right
                    segID = writeSeg(BCFILE,'XMAX_FACE',segID,planeNodeIDs)

            elif r == 2: # zmin/zmax (non-reflecting & user-defined)
                # setup dictionary for zmin / zmax contraint options
                if m == 'bcmax': # zmax
                    if opts.zmax == 'full':
                        writeNodeBC(BCFILE,planeNodeIDs,'1,1,1,1,1,1')
                    elif opts.zmax == 'inplane':
                        writeNodeBC(BCFILE,planeNodeIDs,'0,0,1,1,1,0')
                if m == 'bc': # zmin
                    segID = writeSeg(BCFILE,'ZMIN_FACE',segID,planeNodeIDs)
                    if opts.zmin == 'full':
                        writeNodeBC(BCFILE,planeNodeIDs,'1,1,1,1,1,1')
                    elif opts.zmin == 'inplane':
                        writeNodeBC(BCFILE,planeNodeIDs,'0,0,1,1,1,0')

    # write non-reflecting boundaries (set segment references)
    if(opts.noreflect is True):
        print('Writing non-reflecting boundary segments to %s...' % opts.bcfile)
        BCFILE.write('*BOUNDARY_NON_REFLECTING\n')
        for i in range(1,segID):
            BCFILE.write('%i,0.0,0.0\n' % i)
        BCFILE.write('*END\n')
    else:
        print('No non-reflecting boundary segments written to %s...' % opts.bcfile)

    # close all of our files open for read/write
    BCFILE.close()
'''

#############################################################################################################################
def SortNodeIDs(nic):
    '''
    Sort the node IDs by spatial coordinates into a 3D matrix and return the corresponding axes

    INPUTS:
        nic - nodeIDcoords (n matrix [# nodes x 4, dtype = i4,f4,f4,f4])

    OUTPUTS:
        SortedNodeIDs - n matrix (x,y,z)
        x - array
        y - array
        z - array
    '''

    import numpy as n

    axes = [n.unique(nic['x']), n.unique(nic['y']), n.unique(nic['z'])]
    
    # test to make sure that we have the right dimension (and that precision issues aren't adding extra unique values)
    if len(nic) != (axes[0].size * axes[1].size * axes[2].size):
        sys.exit('ERROR: Dimension mismatch - possible precision error when sorting nodes (?)') 

    # sort the nodes by x, y, then z columns
    I = nic.argsort(order=('x','y','z')) 
    snic = nic[I]
    snic = snic.reshape((axes[0].size,axes[1].size,axes[2].size))  
    
    return [snic, axes]

#############################################################################################################################
def extractPlane(snic,axes,plane):
    '''
    Extract the node IDs on a specified plane from a sorted node ID & coordinate 3D array.

    INPUTS:
        snic - sorted node IDs & coordinates array
        axes - list of unique coordinates in the x, y, and z dimensions
        plane - list:
            index - index of the plane to extract (x=0, y=1, z=2)
            coord - coordinate of the plane to extract (must exist in axes list)

    OUPUTS:
        planeNodeIDs - spatially-sorted 2D node IDs on the specified plane
        
    EXAMPLE: planeNodeIDs = extractPlane(snic,axes,(0,-0.1))
    '''
    if plane[0] == 0:
        planeNodeIDs = snic[axes[plane[0]] == plane[1],:,:]
    elif plane[0] == 1: 
        planeNodeIDs = snic[:,axes[plane[0]] == plane[1],:]
    elif plane[0] == 2: 
        planeNodeIDs = snic[:,:,axes[plane[0]] == plane[1]]
    else:
        sys.exit("ERROR: Specified plane index to extract does not exist")

    planeNodeIDs = planeNodeIDs.squeeze()
    return planeNodeIDs
#############################################################################################################################
def writeSeg(BCFILE,title,segID,planeNodeIDs):
    BCFILE.write('*SET_SEGMENT_TITLE\n')
    BCFILE.write('%s\n' % title)
    BCFILE.write('%i\n' % segID)
    for i in range(0,(len(planeNodeIDs)-1)):
        (a,b) = planeNodeIDs.shape
        for j in range(0,(b-1)):
            BCFILE.write("%i,%i,%i,%i\n" % (planeNodeIDs[i,j][0],planeNodeIDs[i+1,j][0],planeNodeIDs[i+1,j+1][0],planeNodeIDs[i,j+1][0]))
    segID = segID + 1
    return segID
#############################################################################################################################
def writeNodeBC(BCFILE,planeNodeIDs,dofs):
    import pdb
    BCFILE.write('*BOUNDARY_SPC_NODE\n')
    for i in planeNodeIDs: # don't grab the zmin / zmax rows (those will be defined in the zmin/zmax defs)
        for j in i:
            BCFILE.write("%i,0,%s\n" % (j[0],dofs))
#############################################################################################################################
def assemble_bc_face_options(opts,axes):
    '''
    assemble a dictionary of BC face options
    '''
    options = ('xmin','xmax','ymin','ymax','zmin','zmax')
    xyz_indices = (0,0,1,1,2,2)

    bc_face_options={}
    num_sym = 0 # initialize sym count
    bc_face_options['xmin'] = (x,axes[x].min(),opts.xmin)
    num_sym = count_sym(optx.xmin,num_sym)
    bc_face_options['xmax'] = (x,axes[x].max(),opts.xmax)
    num_sym = count_sym(optx.xmin,num_sym)
    bc_face_options['ymin'] = (y,axes[y].min(),opts.ymin)
    num_sym = count_sym(optx.xmin,num_sym)
    bc_face_options['ymax'] = (y,axes[y].max(),opts.ymax)
    num_sym = count_sym(optx.xmin,num_sym)
    bc_face_options['zmin'] = (z,axes[z].min(),opts.zmin)
    num_sym = count_sym(optx.xmin,num_sym)
    bc_face_options['zmax'] = (z,axes[z].max(),opts.zmax)
    num_sym = count_sym(optx.xmin,num_sym)

    # test for quarter or half symmetry
    if num_sym == 2:
        bc_face_options['sym'] = 'qsym'
    elif num_sym == 1:
        bc_face_options['sym'] = 'hsym'
    else:
        bc_face_option['sym'] = None
    
    return bc_face_options

    def count_sym(user_spec, num_sym)
        if user_spec is 'sym':
            num_sym = num_sym + 1 
            sym_loc = (
        return num_sym
#############################################################################################################################
def dyna_boundary_spc_string(bc_option):
    '''
    define the LS-DYNA BOUNDARY_SPC_* string to associate with the specified bc option
    '''
    if bc_option == 'fixed':
        bc_string == '1,1,1,1,1,1'
#############################################################################################################################
    
if __name__ == "__main__":
    main()

