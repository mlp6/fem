#!/usr/local/bin/python2.7
'''
createdat.py - create *.dat file from node ASCII files extracted from d3plot files using extract_node_data.py
'''

__author__ = "Mark Palmeri (mlp6)"
__date__ = "2012-02-14"
__version__ = "0.1"


% INPUTS:   ModelType - 'struct' or 'therm' 
%           NoFiles - number of t*.asc files to convert
%
% OUTPUT: disp/therm.dat is written to CWD
%           All data is float32 with the format:
%               NUM_NODES
%               NUM_DIMS (Node ID, X, Y, Z displacements)
%               NUM_TIMESTEPS
%               The rest of the data are the concatenation of NUM_NODES x NUM_DIMS x NUM_TIMESTEPS.

disp('Reading in ASCII data files . . .');

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
