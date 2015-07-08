// scale_disp_dat.cpp - scale disp.dat displacements by user-specified amount

#include <fstream>
#include <iostream>
using namespace std;

int main () {
    float scaleFactor = 0.1;
    int wordSize = 4;  // 32-bit float
    int headerCount = 3;  // number of header words
    int count = 0;  // float word count
    float value;
    int NUM_NODES;

    // open files for reading and writing
    fstream dispin ("disp.dat", ios::in | ios::binary);
    fstream dispout ("disp_scaled.dat", ios::out | ios::binary);

    while (dispin.read((char*)&value, wordSize)) {
        if (count == 0) {
            NUM_NODES = (int) value;
            dispout.write((char*)&value, wordSize);
            // cout << "Number of nodes: " << NUM_NODES << '\n';
            count++;
            }
        else if (count < (headerCount + NUM_NODES)) {
            dispout.write((char*)&value, wordSize);
            count++;
            }
        else {
            value *= 0.1;
            dispout.write((char*)&value, wordSize);
            count++;
        }
    }

    dispin.close();
    dispout.close();

    return 0;
}
