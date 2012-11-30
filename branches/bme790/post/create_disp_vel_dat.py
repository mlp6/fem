#!/usr/local/bin/python2.7
'''

create_disp_vel_dat.py - create disp.dat and vel.dat files from a nodout file

This is replacing StuctPost, which relied on ls-prepost to extract data from d3plot files, but no longer works gracefully on the cluster w/o GTK/video support.  Also replaced the Matlab scritps, so this should run self-contained w/ less dependencies.

'''

__author__ = "Mark Palmeri (mlp6)"
__date__ = "2012-11-02"
__email__ = "mark.palmeri@duke.edu"

% INPUTS:   ModelType - 'struct' or 'therm' 
%           NoFiles - number of t*.asc files to convert
%
% OUTPUT: disp/therm.dat is written to CWD
%           All data is float32 with the format:
%               NUM_NODES
%               NUM_DIMS (Node ID, X, Y, Z displacements)
%               NUM_TIMESTEPS
%               The rest of the data are the concatenation of NUM_NODES x NUM_DIMS x NUM_TIMESTEPS.


def main():
    import os,sys,math
    import numpy as n
    
    if sys.version < '2.7':
        sys.exit("ERROR: Requires Python >= v2.7")

    import argparse

    # lets read in some command-line arguments
    parser = argparse.ArgumentParser(description="Generate disp.dat and vel.dat data from a nodout files.  \n\nPROG [OPTIONS]...",version="%s" % __version__)
    parser.add_argument("--nefile",dest="nefile",help="new element definition output file [default = struct.dyn]",default="struct.dyn")
    parser.add_argument("--nodout",dest="nodout",help="node definition input file [default = nodes.dyn]",default="nodes.dyn")
    parser.add_argument("--elefile",dest="elefile",help="element definition input file [default = elems.dyn]",default="elems.dyn")
    parser.add_argument("--partid",dest="partid",help="part ID to assign to the new structure [default = 2]",default=2)
    parser.add_argument("--struct",dest="struct",help="type of structure (e.g., sphere, layer) [default = sphere]",default="sphere")
    parser.add_argument("--sopts",dest="sopts",help="structure options (see in-code comments)",nargs='+',type=float)

    args = parser.parse_args()
















% open the DAT file for writing
DISPDAT = 'disp.dat';
disp_fid=fopen(DISPDAT,'w');

for i=1:NoFiles,
        
        % read in data from the ASCII file
        fid = fopen(sprintf('node_disp_t%i.asc',i),'r');
        tempscan = textscan(fid,'%f32%f32%f32%f32','HeaderLines',5,'CommentStyle','*');
        fclose(fid);
        tempmat = cell2mat(tempscan);
        clear tempscan

        % write some numbers to the header to use when reading the data
        if(i == 1),
            numnodes = size(tempmat,1);
            numdims = size(tempmat,2);
            numtimesteps = NoFiles;
            fwrite(disp_fid,numnodes,'float32');
            fwrite(disp_fid,numdims,'float32');
            fwrite(disp_fid,numtimesteps,'float32');
            disp(sprintf('%s headers written',DISPDAT));
        end;

        % write data to DISPDAT; it will be automatically concatenated and can
        % be reshaped on read using the header integers
        fwrite(disp_fid,tempmat,'float32');
            
        clear tempmat

	disp(sprintf('Extracting data from file %i of %i',i,NoFiles));
end;


fclose(disp_fid);

% THIS IS NO LONGER NEEDED SINCE 'float32' DATA IS WRITTEN DIRECTLY TO *.DAT
% convert to double precision to work w/ downstream functions
% disp = double(disp);

%disp('Saving disp.mat file')
disp(sprintf('File Created: %s',DISPDAT))
%save disp.mat disp
