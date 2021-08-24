// scale_disp_dat.cpp - scale disp.dat displacements by user-specified amount

#include <fstream>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
using namespace std;

int main (int argc, char **argv) {
    float scaleFactor = 1.0;
    int wordSize = 4;  // 32-bit float
    int headerCount = 3;  // number of header words
    int count = 0;  // float word count
    float value;
    int NUM_NODES;

    extern char *optarg;
    int opt = 0;
    static char usage[] = "scale_disp_dat [-i disp.dat] [-o disp_scaled.dat] -s scaleFactor\n";
    const char *dispinFilename = "disp.dat";
    const char *dispoutFilename = "disp_scaled.dat";

    if (argc == 1) {
        printf("%s\n", usage);
        exit(EXIT_FAILURE);
    }

    while ((opt = getopt(argc, argv, "i:o:s:")) != -1) {
        switch (opt) {
            case 'i':
                dispinFilename = optarg;
                break;
            case 'o':
                dispoutFilename = optarg;
                break;
            case 's':
                scaleFactor = strtof(optarg, NULL);
                break;
            default:
                printf("%s\n", usage);
                exit(EXIT_FAILURE);
        }
    }

    // let the user know what they told us to use
    printf("Input File: %s\n", dispinFilename);
    printf("Output File: %s\n", dispoutFilename);
    printf("Scale Factor: %f\n", scaleFactor);

    // open files for reading and writing
    fstream dispin (dispinFilename, ios::in | ios::binary);
    fstream dispout (dispoutFilename, ios::out | ios::binary);

    // loop through the file, scaling only the displacement values
    while (dispin.read((char*)&value, wordSize)) {
        if (count == 0) {
            NUM_NODES = (int) value;
            dispout.write((char*)&value, wordSize);
            count++;
            }
        else if (count < (headerCount + NUM_NODES)) {
            dispout.write((char*)&value, wordSize);
            count++;
            }
        else {
            value *= scaleFactor;
            dispout.write((char*)&value, wordSize);
            // reset the counter if we've completed a time step
            if (count == (headerCount + NUM_NODES*4 - 1)) {
                count = headerCount;
            }
            else {
                count++;
            }
        }
    }

    // close the files
    dispin.close();
    dispout.close();

    return 0;
}
