function []=createsimres(dispfile,node_dyn,dyn_file);
% function []=createsimres(dispfile,node_dyn,dyn_file);
%
% Create simres.mat that shares the same format as experimental res*.mat files.
%
% INPUTS:
%   dispfile (string) - path for disp.dat created by createdisp.m
%   node_dyn (string) - path to the node ID & coordinate file (nodes.dyn)
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
% Modified to read individual time steps from the disp.dat binary file so that
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
% changed nodes.asc -> nodes.dyn (i.e., handle header/footer starting with '*'
% Mark 2011-04-21
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% check to make sure the specified files actually exist
if(exist(node_dyn) ~= 2 || exist(dyn_file) ~= 2),
    disp(pwd);
    if(exist(node_dyn) ~= 2),
        warning('%s does not exist',node_dyn);
    end;
    if(exist(dyn_file) ~=2 ),
        warning('%s does not exist',dyn_file);
    end;
    warning('ERROR: res_sim.mat not successfully created');
    return;
end;

% This will now be done in the timestep loop, streamed from the disp.dat file.
% load disp
% load(dispfile);

[SortedNodeIDs,ele,lat,axial]=SortNodeIDs(node_dyn);

% find the imaging plane
ele0 = min(find(ele >= 0));
image_plane = squeeze(SortedNodeIDs(ele0,:,:));

% load in some parameters from disp.dat
if(exist(dispfile,'file') == 0),
    error(sprintf('%s does not exist.  Make sure that (z)disp.mat/dat files are converted to disp.dat .',dispfile));
end;
disp_fid = fopen(dispfile,'r');

NUM_NODES = fread(disp_fid,1,'float32')
NUM_DIMS = fread(disp_fid,1,'float32')
NUM_TIMESTEPS = fread(disp_fid,1,'float32')

%for t=1:size(disp,3),
for t=1:NUM_TIMESTEPS,

    disp(t)
    % extract the disp values for the appropriate time step
    fseek(disp_fid,3*4+NUM_NODES*NUM_DIMS*(t-1)*4,-1);
    disp_slice = fread(disp_fid,NUM_NODES*NUM_DIMS,'float32');
    disp_slice = double(reshape(disp_slice,NUM_NODES,NUM_DIMS));

    %temp(disp(:,1,1)) = disp(:,4,t);
    temp(disp_slice(:,1)) = disp_slice(:,4);
    %temp(disp_slice(:,1)) = disp_slice(:,3);
    temp2 = -temp(image_plane)*1e4;
    temp2 = shiftdim(temp2,1);
    arfidata(:,:,t) = temp2;
    clear temp temp2

end;

% setup the axis and time variables
%t=0:TimeStep:TerminationTime; % s  %GOT RID OF THIS W/ THE 2010-01-24 VERSION
% I really only need the time step size since NUM_TIMESTEPS is being provided by disp.dat, so...
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
