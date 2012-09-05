function []=createdisp(NoFiles)
% function []=createdisp(NoFiles);
%
% INPUTS:  NoFiles - number of t*.asc files to convert
%
% OUTPUT: disp.dat is written to CWD
%           All data is float32 with the format:
%               NUM_NODES
%               NUM_DIMS (Node ID, X, Y, Z displacements)
%               NUM_TIMESTEPS
%               The rest of the data are the concatenation of NUM_NODES x NUM_DIMS x NUM_TIMESTEPS.
%
% Mark Palmeri (mlp6)
% mark.palmeri@duke.edu
% 2009-07-08

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MODIFICATION HISTORY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Originally written
% Mark 05/17/04
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Modified to convert disp to single precision to save
% disk space when saved.
% Mark 04/14/05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2009-07-08
% No longer save a single MAT file that needs to be 
% written/read all at once (consuming lots of RAM);
% now binary data is streamed to a binary *.dat file.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Formerly createzdisp.m - now just createdisp.m; changed
% all references from 'zdisp' -> 'disp'
% Mark Palmeri (mlp6)
% 2010-04-20
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Updaded the number of HeaderLines in the node*.asc
% files outputed from lspp4 to be 6 from 5 (pre v4.x)
% Mark Palmeri (mlp6@duke.edu)
% 2012-09-05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

disp('Reading in ASCII data files . . .');

% open the DAT file for writing
DISPDAT = 'disp.dat';
disp_fid=fopen(DISPDAT,'w');

for i=1:NoFiles,
        
        % read in data from the ASCII file
        fid = fopen(sprintf('node_disp_t%i.asc',i),'r');
        tempscan = textscan(fid,'%f32%f32%f32%f32','HeaderLines',6,'CommentStyle','*');
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
