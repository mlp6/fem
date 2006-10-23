function d3plot_new(n,dynfile,prec, numsplit);
%D3PLOT Generates 3D matrix of nodal coordinates through time
%   d3plot_new(n,filename,precision) generates one or more 3D matrices in a file
%   ('zdisp.mat' by default) that contains the coordinates through time
%   of the nodes in ascending order and a structure that contains the
%   Control Data for the d3plot files. The structure of the matrix is
%   (# of nodes by 4 columns by # of time steps), where the first column
%   is node # and columns 2 -> 4 are the x,y,z coordinates.  
%
%   The data is divided into blocks of 50 time steps  and 
%   are saved as different variables in the zdisp file.
%   (steps 1->50 are zdisp, subsequent blocks of 50 (x->y are zdispx_y),  
%   the remaining time steps are saved in zdisp_rem.)
%
%   n is the integer attached to the last d3plot file ie. d3plot09 (n=9)
%   filename is a character string of the dyna file associated with the d3plot files
%   precision = 1 or 2 (single or double precision)
%
%   For example: Values stored with double precision, the last d3plot
%                file is d3plot101, and the dyna file is dynfile.dyn
%
%       [nodal_coordinates, S] = d3plot(101,'dynfile.dyn',2);
%       -> creates a 3D matrix called nodal_coordinates
%       -> creates a structure S containing the Control Data
%       -> creates default file zdisp.mat with the nodal_coordinates
%       -> time steps 1-50 are in the variable zdisp
%          time steps 51-100 are in the variable zdisp51_100
%          time step 101 is in the variable zdisp_rem
%Paul Toomey 10/24/03
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  edit 6/10/2004 Amy Congdon
% IGNORE ABOVE COMMENTS
%
% INPUT:
% n - number of d3plotN files there are (ie 85, 106, etc)
% dynfile - dynafile for this run
% prec - precision (this is usually 2 for 64 bit words
%
% This creates an output file per numsplit d3plotN files
% in it is: 
% timestep - timesteps for each timestep in the file
% accel - 3D matrix, nodes x [node ID | X accel | Y accel | Z
%          accel] x time. IF no accel data in the model, this is
%          only a 2D matirx of zeros
% coord_out - 3D matrix, nodes x [node ID | X coord | Y coord | Z
%          coord] x time. IF no coordinate data in the model, this is
%          only a 2D matirx of zeros
% temper - 3D matrix, nodes x [node ID | temperature] x time. 
%          IF no temperature data in the model, this is
%          only a 2D matirx of zeros
% vel - 3D matrix, nodes x [node ID | X vel | Y vel | Z
%          vel] x time. IF no velocity data in the model, this is
%          only a 2D matirx of zeros
% 

%Initializing variables
%Pretty sure everything is uint64

basefile='d3plot';
basedir=pwd;
prec = 32*prec;
prec = int2str(prec);
precision = ['uint' prec];

%Checking for a correct input for the # of d3plot files
if n<1
    error('Hey bud, I need a positive number here');
end
if n>999
    error('whoa princess, that is too many files');
end

[node_loc] = read_dyna_nodes(dynfile);

num_nodes = size(node_loc,1);

%Creating CONTROL DATA structure
newfile=[basedir '/' basefile];
fid=fopen(newfile,'r');
B=fread(fid,64,precision);
S=struct('Title',   B(1:10), ...
	 'Runtime', B(11), ...
	 'Date',    B(12), ...
	 'Machine', B(13), ...
	 'Code',    B(14), ...
	 'Version', B(15), ...
	 'NDIM',    B(16), ...
	 'NUMNP',   B(17), ...
	 'ICODE',   B(18), ...
	 'NGLBV',   B(19), ...
	 'IT',      B(20), ...
	 'IU',      B(21), ...
	 'IV',      B(22), ...
	 'IA',      B(23), ...
	 'NEL8',    B(24), ...
	 'NUMMAT8', B(25), ...
	 'BLANK',   B(26), ...
	 'BLANK2',  B(27), ...
	 'NV3D',    B(28), ...
	 'NEL2',    B(29), ...
	 'NUMMAT2', B(30), ...
	 'NV1D',    B(31), ...
	 'NEL4',    B(32), ...
	 'NUMMAT4', B(33), ...
	 'NV2D',    B(34), ...
	 'NEIPH',   B(35), ...
	 'NEIPS',   B(36), ...
	 'MAXINT',  B(37), ...
	 'EDLOPT',  B(38), ...
	 'BLANK3',  B(39), ...
	 'NARBS',   B(40), ...
	 'NELT',    B(41), ...
	 'NUMMATT', B(42), ...
	 'NV3DT',   B(43), ...
	 'IOSHL1',  B(44), ...
	 'IOSHL2',  B(45), ...
	 'IOSHL3',  B(46), ...
	 'IOSHL4',  B(47), ...
	 'BLANKARRAY',B(48:64));

tot_bytes = 64;
%check number of nodes is correct
if S.NUMNP ~= num_nodes
    error('Number of nodes is inconsistant, check precision');
end
%Checking CONTROL DATA to make sure there will be no potential problems when sorting the data
if S.NEL4>0
    error('Number of four node two-dimensional elements is nonzero');
end

%%continue reading file
%pointer at 65th word now

%%%Read in material data if it exists
MATTYP = (S.NDIM == 5);
if (MATTYP)
  NUMRBE=fread(fid, 1, precision);
  NUMMAT=fread(fid, 1, precision);
  IRBTYP=fread(fid, NUMMAT, precision);
  tot_bytes = tot_bytes+2+NUMMAT;
end

%now pointer is at geometry data
%if NDIM = 4 (new Dyna format) then each coordinate is in a 64bit
%float, if NDIM = 3, then each coordinate is 3 ints per 64 bit word

if (S.NDIM==4)
  S.NDIM = 3; %reset NDIM to 3
  precision = ['float' prec];
  Coord=fread(fid,S.NUMNP*S.NDIM,precision);
  IX8 = fread(fid,S.NEL8*9, precision);
  IXT = fread(fid,S.NELT*9, precision);
  IX4 = fread(fid,S.NEL4*5, precision);
  IX2 = fread(fid,S.NEL2*6, precision);
  tot_bytes = tot_bytes + S.NUMNP*S.NDIM + S.NEL8*9 + S.NELT*9 + ...
      S.NEL4*5 + S.NEL2*6;
else
  error('Do not know how to handle old format of Dyna code, please implement')
end

%now pointer at material, node and elem id numbers
arbs = fread(fid, S.NARBS,precision);
tot_byes2 = tot_bytes + S.NARBS;

clear arbs IX8 IXT IX4 IX2;

%determine if anything left in d3plot file
alldata = fread(fid, inf, precision);

%done with d3plot file
status = fclose(fid);


%now we want to read in temp, vel, accel and displacement from
%files. first we need to clean up initial timesteps in alldata
%matrix and then we move onto d3plotN files for remianing information

spinthru = floor(n/numsplit);
leftover = rem(n, numsplit);
NND = (S.IT + S.NDIM*(S.IU + S.IV + S.IA))*S.NUMNP;
info_num = S.IT + S.NDIM*(S.IU + S.IV + S.IA);
ENN = S.NEL8*S.NV3D+S.NEL2*S.NV1D+S.NEL4*S.NV2D;


%first use up alldata information
r=1:S.NUMNP;

x_r=3*r'-2;
y_r=3*r'-1;
z_r=3*r';

coord_out(:,1) = node_loc(:,1);
coord_out(:,2) = Coord(x_r);
coord_out(:,3) = Coord(y_r);
coord_out(:,4) = Coord(z_r);

for (te = 1:size(coord_out, 1))
  temp = (coord_out(te, :) == node_loc(te,:));
  if (temp == 0)
    disp(te)
    error('Node Locations are Wrong');
  end
end

%matrices to hold temperature, velocity, and accel (if they exist)
temper = zeros(S.NUMNP, 2);
temper(:,1) = node_loc(:,1);
vel    = zeros(S.NUMNP, 4);
vel(:,1) = node_loc(:,1);
accel  = zeros(S.NUMNP, 4);
accel(:,1) = node_loc(:,1);

tmstp = 0;

info_size = 1+S.NGLBV+NND+ENN;
steps = floor(size(alldata,1)/info_size);

for ts=1:steps
  tmstp = tmstp + 1;
  timestep(tmstp) = alldata((ts-1)*info_size+1);
  GLOBAL=alldata((ts-1)*info_size+2:(ts-1)*info_size+2+S.NGLBV-1);
  nodedata =alldata((ts-1)*info_size+(2+S.NGLBV):(ts-1)*info_size+(2+S.NGLBV+NND-1));
  elemdata =alldata((ts-1)*info_size+(2+S.NGLBV+NND):ts*info_size);
  index_up = 1;
  matrix_names = ['timestep'];
  
  %put in temps
  if (S.IT)
    temper(:,1,tmstp+1) = node_loc(:,1);
    temper(:,2,tmstp+1) = nodedata(index_up:num_nodes);
    index_up = num_nodes+1;
    matrix_names = [matrix_names ' temper'];
  end
  
  %put in coordinates
  if (S.IU)
    coord_out(:,1,tmstp+1) = node_loc(:,1);
    data_end = index_up+num_nodes*3-1;
    coord_out(:,2,tmstp+1) = nodedata(index_up:3:data_end);
    index_up = index_up+1;
    coord_out(:,3,tmstp+1) = nodedata(index_up:3:data_end);
    index_up = index_up+1;
    coord_out(:,4,tmstp+1) = nodedata(index_up:3:data_end);
    index_up = index_up+num_nodes*3-2;
    matrix_names = [matrix_names ' coord_out'];
  end	
  
  %put in velocities
  if(S.IV)
    vel(:,1,tmstp+1) = node_loc(:,1);
    data_end = index_up+num_nodes*3-1;
    vel(:,2,tmstp+1) = nodedata(index_up:3:data_end);
    index_up = index_up+1;
    vel(:,3,tmstp+1) = nodedata(index_up:3:data_end);
    index_up = index_up+1;
    vel(:,4,tmstp+1) = nodedata(index_up:3:data_end);
    index_up = index_up+num_nodes*3-2;
    matrix_names = [matrix_names ' vel'];
  end	
  
  %put in accel
  if(S.IA)
    accel(:,1,tmstp+1) = node_loc(:,1);
    data_end = index_up+num_nodes*3-1;
    accel(:,2,tmstp+1) = nodedata(index_up:3:data_end);
    index_up = index_up+1;
    accel(:,3,tmstp+1) = nodedata(index_up:3:data_end);
    index_up = index_up+1;
    accel(:,4,tmstp+1) = nodedata(index_up:3:data_end);
    index_up = index_up+num_nodes*3-2;
    matrix_names = [matrix_names ' accel'];
  end	
  
end

eval(sprintf('save zout_first %s', matrix_names));
clear coord_out vel accel temper timestep;

%now put in the rest of the information from d3plotN files
if (spinthru > 0)
for (idx = 1:spinthru)
  %%put Coord and node IDs into a matirx [node ID, X val, Y val, Z val]
  r=1:S.NUMNP;
  
  x_r=3*r'-2;
  y_r=3*r'-1;
  z_r=3*r';
  
  coord_out(:,1) = node_loc(:,1);
  coord_out(:,2) = Coord(x_r);
  coord_out(:,3) = Coord(y_r);
  coord_out(:,4) = Coord(z_r);
  
  for (te = 1:size(coord_out, 1))
    temp = (coord_out(te, :) == node_loc(te,:));
    if (temp == 0)
      disp(te)
      error('Node Locations are Wrong');
    end
  end

  
  %matrices to hold temperature, velocity, and accel (if they exist)
  temper = zeros(S.NUMNP, 2);
  temper(:,1) = node_loc(:,1);
  vel    = zeros(S.NUMNP, 4);
  vel(:,1) = node_loc(:,1);
  accel  = zeros(S.NUMNP, 4);
  accel(:,1) = node_loc(:,1);
  
  start_idx = (idx-1)*numsplit+1;
  idx_end = idx*numsplit;
  savefile = sprintf('zout_%d_to_%d', start_idx, idx_end);
  tmstp = 0;
  
  for i=1:numsplit
    
    if ((i+start_idx-1) < 10)
      filenum = ['0' int2str(i+start_idx-1)]
    else
      filenum = int2str(i+start_idx-1)
    end
    
    newfile=[basedir '/' basefile filenum];
    fid=fopen(newfile,'r');
    
    %read in entire file
    %alldata = fread(fid, inf, precision);
    %find out how many timesteps in file
    d2 = dir(newfile);
    info_size = 1+S.NGLBV+NND+ENN;
    %steps = floor(size(alldata,1)/info_size);
    steps = floor(d2.bytes/8/info_size);
    
    for (ts = 1:steps)
      tmstp = tmstp + 1;
      %timestep(tmstp) = alldata((ts-1)*info_size+1);
      timestep = fread(fid, 1, precision);
      
      %GLOBAL=alldata((ts-1)*info_size+2:(ts-1)*info_size+2+S.NGLBV-1);
      GLOBAL = fread(fid, S.NGLBV, precision);
      
      %nodedata =alldata((ts-1)*info_size+(2+S.NGLBV):(ts-1)*info_size+(2+S.NGLBV+NND-1));
      nodedata = fread(fid, NND, precision);
      
      %elemdata =
      %alldata((ts-1)*info_size+(2+S.NGLBV+NND):ts*info_size);
      elemdata = fread(fid, ENN, precision);
    
      index_up = 1;
      matrix_names = ['timestep'];
      
      %put in temps
      if (S.IT)
	temper(:,1,tmstp+1) = node_loc(:,1);
	temper(:,2,tmstp+1) = nodedata(index_up:num_nodes);
	index_up = num_nodes+1;
	matrix_names = [matrix_names ' temper'];
      end
    
      %put in coordinates
      if (S.IU)
	coord_out(:,1,tmstp+1) = node_loc(:,1);
	data_end = index_up+num_nodes*3-1;
	coord_out(:,2,tmstp+1) = nodedata(index_up:3:data_end);
	index_up = index_up+1;
	coord_out(:,3,tmstp+1) = nodedata(index_up:3:data_end);
	index_up = index_up+1;
	coord_out(:,4,tmstp+1) = nodedata(index_up:3:data_end);
	index_up = index_up+num_nodes*3-2;
	matrix_names = [matrix_names ' coord_out'];
      end	
    
      %put in velocities
      if(S.IV)
	vel(:,1,tmstp+1) = node_loc(:,1);
	data_end = index_up+num_nodes*3-1;
	vel(:,2,tmstp+1) = nodedata(index_up:3:data_end);
	index_up = index_up+1;
	vel(:,3,tmstp+1) = nodedata(index_up:3:data_end);
	index_up = index_up+1;
	vel(:,4,tmstp+1) = nodedata(index_up:3:data_end);
	index_up = index_up+num_nodes*3-2;
	matrix_names = [matrix_names ' vel'];
      end	
      
      %put in accel
      if(S.IA)
	accel(:,1,tmstp+1) = node_loc(:,1);
	data_end = index_up+num_nodes*3-1;
	accel(:,2,tmstp+1) = nodedata(index_up:3:data_end);
	index_up = index_up+1;
	accel(:,3,tmstp+1) = nodedata(index_up:3:data_end);
	index_up = index_up+1;
	accel(:,4,tmstp+1) = nodedata(index_up:3:data_end);
	index_up = index_up+num_nodes*3-2;
	matrix_names = [matrix_names ' accel'];
      end	
     
    end
      
    status = fclose(fid);
  end 
  
  eval(sprintf('save %s %s', savefile, matrix_names));
  clear coord_out vel accel temper timestep;
end
end
  
%handle remainder files
if (leftover > 0)
  %%put Coord and node IDs into a matirx [node ID, X val, Y val, Z val]
  r=1:S.NUMNP;
  
  x_r=3*r'-2;
  y_r=3*r'-1;
  z_r=3*r';
  
  coord_out(:,1) = node_loc(:,1);
  coord_out(:,2) = Coord(x_r);
  coord_out(:,3) = Coord(y_r);
  coord_out(:,4) = Coord(z_r);
  
  %matrices to hold temperature, velocity, and accel (if they exist)
  temper = zeros(S.NUMNP, 2);
  temper(:,1) = node_loc(:,1);
  vel    = zeros(S.NUMNP, 4);
  vel(:,1) = node_loc(:,1);
  accel  = zeros(S.NUMNP, 4);
  accel(:,1) = node_loc(:,1);
  
  start_idx = spinthru*numsplit+1
  idx_end = spinthru*numsplit+leftover;
  savefile = sprintf('zout_%d_to_%d', start_idx, idx_end);
  for i=1:leftover
    if ((i+start_idx-1) < 10)
      filenum = ['0' int2str(i+start_idx-1)]
    else
      filenum = int2str(i+start_idx-1)
    end
    
    newfile=[basedir '/' basefile filenum];
    fid=fopen(newfile,'r');
    timestep(i) = fread(fid, 1, precision);
    GLOBAL=fread(fid,S.NGLBV,precision);
    nodedata = fread(fid, NND, precision);
    
    index_up = 1;
    matrix_names = ['timestep'];
    %put in temps
    if (S.IT)
      temper(:,1,i+1) = node_loc(:,1);
      temper(:,2,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      matrix_names = [matrix_names ' temper'];
    end
    
    %put in coordinates
    if (S.IU)
      coord_out(:,1,i+1) = node_loc(:,1);
      coord_out(:,2,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      coord_out(:,3,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      coord_out(:,4,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      matrix_names = [matrix_names ' coord_out'];
    end	
    
    %put in velocities
    if(S.IV)
      vel(:,1,i+1) = node_loc(:,1);
      vel(:,2,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      vel(:,3,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      vel(:,4,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      matrix_names = [matrix_names ' vel'];
    end	
    
    %put in accel
    if(S.IA)
      accel(:,1,i+1) = node_loc(:,1);
      accel(:,2,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      accel(:,3,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      accel(:,4,i+1) = nodedata(index_up:info_num:end);
      index_up = index_up+1;
      matrix_names = [matrix_names ' accel'];
    end	
    
  status = fclose(fid);
  end
  
  eval(sprintf('save %s %s', savefile, matrix_names));
  clear coord_out vel accel temper timestamp;
end
