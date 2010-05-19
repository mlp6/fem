function [matrix,S] = d3plot(n,nodefile,prec);
% D3PLOT Generates 3D matrix of nodal coordinates through time
%   d3plot(n,filename,precision) generates a 3D matrix in a file
%   ('zdisp.mat' by default) that contains the coordinates through time
%   of the nodes in ascending order and a structure that contains the 
%   Control Data for the d3plot files. The structure of the matrix is 
%   (# of nodes by 4 columns by # of time steps), where the first column 
%   is node # and columns 2 -> 4 are the x,y,z coordinates.
%   
%		INPUTS:
%   n is the integer attached to the last d3plot file ie. d3plot09 (n=9)
%   nodefile is a character string of the dyna file associated
%   with the d3plot files (containing *NODE data)
%   precision = 1 or 2 (single or double precision)
%
%   For example: Values stored with double precision, the last d3plot
%                file is d3plot101, and the dyna file is grant.dyn
%
%       [nodal_coordinates, S] = d3plot(101,'grant.dyn',2);
%       -> creates a 3D matrix called nodal_coordinates
%       -> creates a structure S containing the Control Data
%       -> creates default file zdisp.mat with the nodal_coordinates
%
%
% Paul Toomey 8/20/03
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Updated to be more compatible with new version of ls-dyna
% Mark 04/13/05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Initializing variables
d='d3plot';
file = pwd;
prec = 32*prec;
prec = int2str(prec);
precision = ['uint' prec];

% Checking for a correct input for the # of d3plot files
if n<1
	error('Negative number of files specified!');
end
if n>999
	error('Too many files to process!');
end

% Creating CONTROL DATA structure
newfile=[file '/' d];
fid=fopen(newfile,'r');
B=fread(fid,52,precision);
S=struct('Title',B(1:10),'Runtime',B(11),'Date',B(12),'Machine',B(13),'Code',B(14),'Version',B(15),'NDIM',B(16),'NUMNP',B(17),'ICODE',B(18),'NGLBV',B(19),'IT',B(20),'IU',B(21),'IV',B(22),'IA',B(23),'NEL8',B(24),'NUMMAT8',B(25),'BLANK',B(26),'BLANK2',B(27),'NV3D',B(28),'NEL2',B(29),'NUMMAT2',B(30),'NV1D',B(31),'NEL4',B(32),'NUMMAT4',B(33),'NV2D',B(34),'NEIPH',B(35),'NEIPS',B(36),'MAXINT',B(37),'EDLOPT',B(38),'NMSPH',B(39),'NGPSPH',B(40),'NARBS',B(41),'NELT',B(42),'NUMMATT',B(43),'NV3DT',B(44),'IOSHL1',B(45),'IOSHL2',B(46),'IOSHL4',B(47),'IALEMAT',B(48),'NCFDV',B(49),'NCFDV2',B(50),'NADAPT',B(51),'BLANK3',B(52));
status = fclose(fid);

% Checking CONTROL DATA to make sure there will be no potential
% problems when sorting the data
if S.NEL4>0
	error('Number of four node two-dimensional elements is nonzero');
end

if S.IALEMAT~=0
	error('Fluid material number used for solid element mesh is nonzero');
end
    
if S.NMSPH>0
	error('Number of SPH Nodes is nonzero');
end

precision = ['float' prec];
% Reading in from the d3plot files and creating a 2D matrix
% called Coord with the x,y,z nodal coordinates
newfile=[file '/' d];
fid=fopen(newfile,'r');
B=fread(fid,S.NUMNP*3+64,precision);
Coord=B(65:S.NUMNP*3+64);
        
if n<10
	for i=1:n
		newfile=[file '/' d '0' int2str(i)];
		fid=fopen(newfile,'r');
		B=fread(fid,S.NUMNP*3+21,precision);
		B=B(22:S.NUMNP*3+21);
		Coord=[Coord B];
		status = fclose(fid);
	end
else
	for i=1:9
		newfile=[file '/' d '0' int2str(i)];
		fid=fopen(newfile,'r');
		B=fread(fid,S.NUMNP*3+21,precision);
		B=B(22:S.NUMNP*3+21);
		Coord=[Coord B];
		status = fclose(fid);
	end
	for i=10:n
		newfile=[file '/' d int2str(i)];
		fid=fopen(newfile,'r');
		B=fread(fid,S.NUMNP*3+21,precision);
		B=B(22:S.NUMNP*3+21);
		Coord=[Coord B];
		status = fclose(fid);
	end
end

% Reading from the dyna file to find which nodes are used

newfile=[nodefile];
endofline=sprintf('\n');
  
% Open file
fid=fopen(newfile,'r');
if (fid == -1),
	disp(['Can''t open ' newfile]);
	return;
end;
 
% find last word just before data... 
s=fscanf(fid,'%s',1);
while (~strcmp(s,'*NODE')),
	s=fscanf(fid,'%s',1);
end;

% Find start of next line...        
c=fscanf(fid,'%c',1);
while(c~=endofline);
	c=fscanf(fid,'%c',1);
end;

% Suck in data...  
[node_loc,count]=fscanf(fid,'%d %f %f %f',[4,inf]);
node_loc=node_loc';
fclose(fid);


% Sorting data into the x,y,z components
r=1:S.NUMNP;
x_r=3*r'-2;
y_r=3*r'-1;
z_r=3*r';

x_orig=Coord(x_r,1);
y_orig=Coord(y_r,1);
z_orig=Coord(z_r,1);
x_value=Coord(x_r,1:n+1);
y_value=Coord(y_r,1:n+1);
z_value=Coord(z_r,1:n+1);

% Creating 3D matrix
for w=1:n+1
	matrix(:,1,w)=node_loc(:,1);
end

for r=1:n+1
	matrix(:,2,r)=x_value(:,r)-x_orig;
	matrix(:,3,r)=y_value(:,r)-y_orig;
	matrix(:,4,r)=z_value(:,r)-z_orig;
end

% Creating default zdisp.mat file
zdisp = matrix;
whos zdisp;
save zdisp.mat zdisp
