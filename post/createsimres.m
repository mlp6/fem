function []=createsimres(dispfile, node_dyn, dyn_file, legacynodes);
% function []=createsimres(dispfile,node_dyn,dyn_file, legacynodes);
%
% Create simres.mat that shares the same format as experimental res*.mat files.
%
% INPUTS:
%   dispfile (string) - path for disp.dat created by create_disp_vel_dat.py
%   node_dyn (string) - path to the node ID & coordinate file (nodes.dyn)
%   dyn_file (string) - path to the input dyna deck that includes the d3plot time step
%   legacynodes (boolean) - does disp.dat not have the node IDs repeated every timestep
% 
% OUTPUTS:
%   Saves the file sim_res.mat to the CWD.
%
% Requires the function SortNodeIDs.m 
%
% Mark Palmeri (mlp6)
% 2015-07-23
%

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

[SortedNodeIDs,ele,lat,axial]=SortNodeIDs(node_dyn);

% find the imaging plane
ele0 = min(find(ele >= 0));
image_plane = squeeze(SortedNodeIDs(ele0,:,:));

% load in some parameters from disp.dat
try
    disp_fid = fopen(dispfile,'r');
catch exception
    error(sprintf('ERROR: %s does not exist (created by create_disp_vel_dat.py).',dispfile));
end

NUM_NODES = fread(disp_fid,1,'float32')
NUM_DIMS = fread(disp_fid,1,'float32')
NUM_TIMESTEPS = fread(disp_fid,1,'float32')

[arfidata] = extract_binary_data(disp_fid, NUM_NODES, NUM_DIMS, NUM_TIMESTEPS, image_plane, legacynodes);

TimeStep = extract_TimeStep(dyn_file);
t = [0:(NUM_TIMESTEPS-1)].*TimeStep;
axial = -axial';
axial = axial*10; % convert to mm
lat = lat';
lat = lat*10; % convert to mm

% convert variables to singles
arfidata = single(arfidata);
lat = single(lat);
axial = single(axial);
t = single(t);
save res_sim.mat arfidata lat axial t

function [binary_data_out] = extract_binary_data(fid, NUM_NODES, NUM_DIMS, NUM_TIMESTEPS, image_plane, legacynodes)

    headerWords = 3*4;
    
    for t=1:NUM_TIMESTEPS,
        disp(t)
        % extract the disp values for the appropriate time step
        if (t == 1 | legacynodes),
            fseek(fid, headerWords + NUM_NODES*NUM_DIMS*(t-1)*4, -1);
            disp_slice = fread(fid,NUM_NODES*NUM_DIMS, 'float32');
            disp_slice = double(reshape(disp_slice,NUM_NODES,NUM_DIMS));
            % extract the node IDs on the image plane and save
            nodeIDlist= disp_slice(:,1);
            % reduce disp_slice to just have the x,y,z disps
            disp_slice = disp_slice(:,2:4);
        % node IDs are _not_ saved after the first timestep in latest disp.dat files
        % (flagged by legacynodes boolean)
        else,
            fseek(fid, headerWords + NUM_NODES*NUM_DIMS*4 + NUM_NODES*(NUM_DIMS-1)*4*(t-2), -1);
            disp_slice = fread(fid, NUM_NODES*(NUM_DIMS-1), 'float32');
            disp_slice = double(reshape(disp_slice, NUM_NODES, (NUM_DIMS-1)));
        end
        
        temp(nodeIDlist) = disp_slice(:, 3);
        temp2 = -temp(image_plane)*1e4;
        temp2 = shiftdim(temp2, 1);
        binary_data_out(:,:,t) = temp2;
        clear temp temp2
    end

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
