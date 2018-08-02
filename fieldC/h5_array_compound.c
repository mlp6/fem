/*
 * This example shows how to create a compound data type with an array member,
 * and write an array which has the compound data type to the file.
 *
 * works for FieldParams struct that has an array of structs inside.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <hdf5.h>
#include "field.h"

#define FILE          "dyna.mat"
#define DATASETNAME   "FIELD_PARAMS"
#define LENGTH        10
#define RANK          1
#define ARRAY_RANK    1
#define ARRAY_DIM     3 


int
main(void)
{
int i, numNodes;
point_type focus;
char *nodeName;
char *elemName;
int lowNslow;
int forceNonLinear;
hsize_t dim = 1;

struct nodeEntry *pointsAndNodes, *readMpn(), *temp;
struct FieldParams fieldParams;

hid_t      file, dataset, space; /* Handles */
hid_t      array_tid, array_tid1; /* Array datatype handle */
hid_t      s1_tid;     /* File datatype identifier */
herr_t     status;


	nodeName = "./myNodesShort.dyn";
	fieldParams.alpha = 0.5;
	fieldParams.fnum = 1.3;

	focus.x = 0;
	focus.y = 0;
	focus.z = 0.02;
	fieldParams.focus = focus;

	fieldParams.frequency = 7.2;
	fieldParams.transducer = "vf105";
	fieldParams.impulse = "gaussian";
	fieldParams.soundSpeed = 1540;
	fieldParams.samplingFrequency = 100e6;
	fieldParams.threads = 1;

	fieldParams.pointsAndNodes = readMpn(nodeName, &numNodes);

	fprintf(stderr, "after readMpn; numNodes %d\n", numNodes);
	fprintf(stderr, "%f %f %f %f\n", fieldParams.pointsAndNodes[0].nodeID, fieldParams.pointsAndNodes[0].x, fieldParams.pointsAndNodes[0].y, fieldParams.pointsAndNodes[0].z);


    /*
     * Create the data space.
     */
    space = H5Screate_simple(RANK, &dim, NULL);

    /*
     * Create the file.
     */
    file = H5Fcreate(FILE, H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);

    /*
     * Create the array data type. 
     */
hsize_t nodes[] = {10, 4};

fprintf(stderr, "nodes[0] is %d\n", nodes[0]);

     array_tid1 = H5Tarray_create(H5T_NATIVE_DOUBLE, 2, nodes);

    /*
     * Create the memory data type. 
     */
	i = sizeof(double) + numNodes * 3 * 10 * sizeof(double);

	fprintf(stderr, "i is %d\n", i);

    s1_tid = H5Tcreate (H5T_COMPOUND, i);
    H5Tinsert(s1_tid, "alpha", HOFFSET(struct FieldParams, alpha), H5T_NATIVE_DOUBLE);
    H5Tinsert(s1_tid, "pointsAndNodes", HOFFSET(struct FieldParams, pointsAndNodes), array_tid1);

    /* 
     * Create the dataset.
     */
    dataset = H5Dcreate(file, DATASETNAME, s1_tid, space, H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);

    /*
     * Wtite data to the dataset; 
     */
    status = H5Dwrite(dataset, s1_tid, H5S_ALL, H5S_ALL, H5P_DEFAULT, &fieldParams);

    /*
     * Release resources
     */
    H5Tclose(s1_tid);
    H5Tclose(array_tid1);
    H5Sclose(space);
    H5Dclose(dataset);
    H5Fclose(file);
 
#if 0
#endif

    return 0;
}
