function []=createsimres(zdispfile,node_asc,dyn_file);
% function []=createsimres(zdispfile,node_asc,dyn_file);
%
% Create simres.mat that shares the same format as experimental res*.mat files.
%
% INPUTS:
%   zdispfile (string) - path for zdisp.dat created by createzdisp.m
%   node_asc (string) - path to the node ID & coordinate ASCII file (no dyna
%                       headers/footers)
%   dyn_file (string) - path to the input dyna deck that includes the d3plot time step
%
%   Requires the function SortNodeIDs.m - should be in the svn repository.
% 
% OUTPUTS:
%   Saves the file sim_res.mat to the CWD.
%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MODIFICATION HISTORY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Originally written
% Mark 03/07/08
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2009-07-08
% Modified to read individual time steps from the zdisp.dat binary file so that
% large chunks of RAM are needed.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2010-01-24 (Mark)
% (1) Very annoying to have to enter the 'TimeStep' and 'TerminationTime' as inputs
% when you are trying to batch a job; so, that has been "upgraded" to now read
% those values from the dyna deck, which is now an input.  Assumptions about 
% reading in that data automatically are detailed below.
%
% (2) Added more graceful error-checking upfront (checking that input files exist)
% to allow batch jobs to run completely even with some missing files along the way. 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% check to make sure the specified files actually exist
if(exist(node_asc) ~= 2 || exist(dyn_file) ~= 2),
    disp(pwd);
    if(exist(node_asc) ~= 2),
        warning('%s does not exist',node_asc);
    end;
    if(exist(dyn_file) ~=2 ),
        warning('%s does not exist',dyn_file);
    end;
    warning('ERROR: res_sim.mat not successfully created');
    return;
end;

% This will now be done in the timestep loop, streamed from the zdisp.dat file.
% load zdisp
% load(zdispfile);

[SortedNodeIDs,ele,lat,axial]=SortNodeIDs(node_asc);

% find the imaging plane
ele0 = min(find(ele >= 0));
image_plane = squeeze(SortedNodeIDs(ele0,:,:));

% load in some parameters from zdisp.dat
if(exist(zdispfile,'file') == 0),
    error(sprintf('%s does not exist.  Make sure that zdisp.mat files are converted to zdisp.dat .',zdispfile));
end;
zdisp_fid = fopen(zdispfile,'r');

NUM_NODES = fread(zdisp_fid,1,'float32');
NUM_DIMS = fread(zdisp_fid,1,'float32');
NUM_TIMESTEPS = fread(zdisp_fid,1,'float32');

%for t=1:size(zdisp,3),
for t=1:NUM_TIMESTEPS,

    % extract the zdisp values for the appropriate time step
    fseek(zdisp_fid,3*4+NUM_NODES*NUM_DIMS*(t-1)*4,-1);
    zdisp_slice = fread(zdisp_fid,NUM_NODES*NUM_DIMS,'float32');
    zdisp_slice = double(reshape(zdisp_slice,NUM_NODES,NUM_DIMS));

    %temp(zdisp(:,1,1)) = zdisp(:,4,t);
    temp(zdisp_slice(:,1)) = zdisp_slice(:,4);
    temp2 = -temp(image_plane)*1e4;
    temp2 = shiftdim(temp2,1);
    arfidata(:,:,t) = temp2;

end;

% setup the axis and time variables
%t=0:TimeStep:TerminationTime; % s  %GOT RID OF THIS W/ THE 2010-01-24 VERSION
% I really only need the time step size since NUM_TIMESTEPS is being provided by zdisp.dat, so...
TimeStep = extract_TimeStep(dyn_file);
t = [0:(NUM_TIMESTEPS-1)].*TimeStep;
axial = -axial';
axial = axial*10; % convert to mm
lat = lat';
lat = lat*10; % convert to mm

% 2010-01-24 -> shouldn't need this anymore since NUM_TIMESTEPS is being used to define 
% the 't' variable
%
% make sure that the correct number of time steps are in the 't' variable - if
% not, truncate ones off the end b/c the number of dumped time steps can come
% up one short from the calculated number of data dumps
%if(length(t) ~= size(arfidata,3)),
%    if(length(t) < size(arfidata,3)),
%        arfidata = arfidata(:,:,1:length(t));
%    else,
%        t = t(1:size(arfidata,3));
%    end;
%end;

% convert variables to singles
arfidata = single(arfidata);
lat = single(lat);
axial = single(axial);
t = single(t);

save res_sim.mat arfidata lat axial t

function [TimeStep]=extract_TimeStep(dyn_file)
fid = fopen(dyn_file);
hit = 0;
while(hit ~= 2),
    dyn_line = fgetl(fid);
    if(strcmp(dyn_line,'*DATABASE_BINARY_D3PLOT')),
        hit = 1;
    end;
    % once we found the correct control card, we're assuming the first entry on the next
    % non-comment line is the time step that we want in seconds
    while(hit==1), 
        next_line = fgetl(fid);
        split_next_line = regexp(next_line,',','split');
        first_entry = split_next_line{1};
        first_char = first_entry(1);
        if(strcmp(first_char,'$')),
            continue;
        else,
            TimeStep = first_entry;
            TimeStep = str2num(TimeStep)
            return
        end;
    end;
end;
fclose(fid);
