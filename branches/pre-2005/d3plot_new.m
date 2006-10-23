function [matrix,S] = d3plot(n,grant,prec);
%D3PLOT Generates 3D matrix of nodal coordinates through time
%   d3plot(n,filename,precision) generates one or more 3D matrices in a file
%   ('zdisp.mat' by default) that contains the coordinates through time
%   of the nodes in ascending order and a structure that contains the
%   Control Data for the d3plot files. The structure of the matrix is
%   (# of nodes by 4 columns by # of time steps), where the first column
%   is node # and columns 2 -> 4 are the x,y,z coordinates.  

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
%                file is d3plot101, and the dyna file is grant.dyn
%
%       [nodal_coordinates, S] = d3plot(101,'grant.dyn',2);
%       -> creates a 3D matrix called nodal_coordinates
%       -> creates a structure S containing the Control Data
%       -> creates default file zdisp.mat with the nodal_coordinates
%       -> time steps 1-50 are in the variable zdisp
%          time steps 51-100 are in the variable zdisp51_100
%          time step 101 is in the variable zdisp_rem
%Paul Toomey 10/24/03

%Initializing variables
d='d3plot';
file=pwd;
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

%Creating CONTROL DATA structure
newfile=[file '/' d];
fid=fopen(newfile,'r');
B=fread(fid,52,precision);
S=struct('Title',B(1:10),'Runtime',B(11),'Date',B(12),'Machine',B(13),'Code',B(14),'Version',B(15),'NDIM',B(16),'NUMNP',B(17),'ICODE',B(18),'NGLBV',B(19),'IT',B(20),'IU',B(21),'IV',B(22),'IA',B(23),'NEL8',B(24),'NUMMAT8',B(25),'BLANK',B(26),'BLANK2',B(27),'NV3D',B(28),'NEL2',B(29),'NUMMAT2',B(30),'NV1D',B(31),'NEL4',B(32),'NUMMAT4',B(33),'NV2D',B(34),'NEIPH',B(35),'NEIPS',B(36),'MAXINT',B(37),'EDLOPT',B(38),'NMSPH',B(39),'NGPSPH',B(40),'NARBS',B(41),'NELT',B(42),'NUMMATT',B(43),'NV3DT',B(44),'IOSHL1',B(45),'IOSHL2',B(46),'IOSHL4',B(47),'IALEMAT',B(48),'NCFDV',B(49),'NCFDV2',B(50),'NADAPT',B(51),'BLANK3',B(52));
status = fclose(fid);

%Checking CONTROL DATA to make sure there will be no potential problems when sorting the data
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
%Reading in from the d3plot files and creating a 2D matrix called Coord with the x,y,z nodal coordinates
disp('Reading data...');
        newfile=[file '/' d];
        fid=fopen(newfile,'r');
        B=fread(fid,S.NUMNP*3+64,precision);
        Coord=B(65:S.NUMNP*3+64);
if n<10
    for i=2:n
        newfile=[file '/' d '0' int2str(i)];
        fid=fopen(newfile,'r');
        B=fread(fid,S.NUMNP*3+21,precision);
        B=B(22:S.NUMNP*3+21);
        Coord=[Coord B];
        status = fclose(fid);
    end
else
    for i=2:9
        newfile=[file '/' d '0' int2str(i)];
        fid=fopen(newfile,'r');
        B=fread(fid,S.NUMNP*3+21,precision);
        B=B(22:S.NUMNP*3+21);
        Coord=[Coord B];
        status = fclose(fid);
    end
    if n>50
        lim=50;
    end
    for i=10:lim
        newfile=[file '/' d int2str(i)];
        fid=fopen(newfile,'r');
        B=fread(fid,S.NUMNP*3+21,precision);
        B=B(22:S.NUMNP*3+21);
        Coord=[Coord B];
        status = fclose(fid);
    end
    
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
%Reading from the dyna file to find which nodes are used
newfile=[file '/' grant];
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
                                                                                                                            
                                                                                                                            
%Sorting data into the x,y,z components                                                                                     
disp('Sorting data...');
r=1:S.NUMNP;                                                                                                                
x_r=3*r'-2;
y_r=3*r'-1;                                                                                                                 
z_r=3*r';

x_orig=Coord(x_r,1);
y_orig=Coord(y_r,1);
z_orig=Coord(z_r,1);
x_value=Coord(x_r,1:lim);
y_value=Coord(y_r,1:lim);
z_value=Coord(z_r,1:lim);


%Creating 3D matrix
for w=1:lim
    matrix(:,1,w)=node_loc(:,1);
end

for r=1:lim
    matrix(:,2,r)=x_value(:,r)-x_orig;
    matrix(:,3,r)=y_value(:,r)-y_orig;
    matrix(:,4,r)=z_value(:,r)-z_orig;
end

%Creating default zdisp.mat file
zdisp = matrix;
save zdisp.mat zdisp
clear matrix; clear Coord; clear zdisp;
end

%%%files more than 50 time steps%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    y=(n-rem(n,50))/50;
    for j=2:y
        disp('Reading data...');
        newfile=[file '/' d '51'];
        fid=fopen(newfile,'r');
        B=fread(fid,S.NUMNP*3+21,precision);
        B=B(22:S.NUMNP*3+21);
        Coord=B;
        status = fclose(fid);
        for i=(j-1)*50+2:j*50
            newfile=[file '/' d int2str(i)];
            fid=fopen(newfile,'r');
            B=fread(fid,S.NUMNP*3+21,precision);
            B=B(22:S.NUMNP*3+21);
            Coord=[Coord B];
            status = fclose(fid);
        end
%Reading from the dyna file to find which nodes are used

newfile=[file '/' grant];
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
                                                                                                                            
                                                                                                                            
%Sorting data into the x,y,z components                                                                                     
disp('Sorting data...');
r=1:S.NUMNP;                                                                                                                
x_r=3*r'-2;
y_r=3*r'-1;                                                                                                                 
z_r=3*r';

x_orig=Coord(x_r,1);
y_orig=Coord(y_r,1);
z_orig=Coord(z_r,1);
x_value=Coord(x_r,1:50);
y_value=Coord(y_r,1:50);
z_value=Coord(z_r,1:50);

%Creating 3D matrix
for w=1:50
    matrix(:,1,w)=node_loc(:,1);
end

for r=1:50
    matrix(:,2,r)=x_value(:,r)-x_orig;
    matrix(:,3,r)=y_value(:,r)-y_orig;
    matrix(:,4,r)=z_value(:,r)-z_orig;
end

%Creating default zdisp.mat file
switch j
case 2 
    zdisp51_100=matrix;
    save zdisp51_100.mat zdisp51_100;
    clear zdisp51_100; clear matrix;
case 3
    zdisp101_150=matrix;
    save zdisp101_150.mat zdisp101_150;
    clear zdisp101_150; clear matrix;
case 4
    zdisp151_200=matrix;
    save zdisp151_200.mat zdisp151_200;
    clear zdisp151_200; clear matrix;
case 5
    zdisp201_250=matrix;
    save zdisp201_250.mat zdisp201_250;
    clear zdisp201_250; clear matrix;
case 6
    zdisp251_300=matrix;
    save zdisp251_300.mat zdisp251_300;
    clear zdisp251_300; clear matrix;
case 7
    zdisp301_350=matrix;
    save zdisp301_350.mat zdisp301_350;
    clear zdisp301_350; clear matrix;
case 8
    zdisp351_400=matrix;
    save zdisp351_400.mat zdisp351_400;
    clear zdisp351_400; clear matrix;
case 9
    zdisp401_450=matrix;
    save zdisp401_450.mat zdisp401_450;
    clear zdisp401_450; clear matrix;
case 10
    zdisp451_500=matrix;
    save zdisp451_500.mat zdisp451_500;
    clear zdisp451_500; clear matrix;
case 11
    zdisp501_550=matrix;
    save zdisp501_550.mat zdisp501_550;
    clear zdisp501_550; clear matrix;
case 12
    zdisp551_600=matrix;
    save zdisp551_600.mat zdisp551_600;
    clear zdisp551_600; clear matrix;
case 13
    zdisp601_650=matrix;
    save zdisp601_650.mat zdisp601_650;
    clear zdisp601_650; clear matrix;
case 14
    zdisp651_700=matrix;
    save zdisp651_700.mat zdisp651_700;
    clear zdisp651_700; clear matrix;
case 15
    zdisp701_750=matrix;
    save zdisp701_750.mat zdisp701_750;
    clear zdisp701_750; clear matrix;
case 16
    zdisp751_800=matrix;
    save zdisp751_800.mat zdisp751_800;
    clear zdisp751_800; clear matrix;
case 17
    zdisp801_850=matrix;
    save zdisp801_850.mat zdisp801_850;
    clear zdisp801_850; clear matrix;
case 18
    zdisp851_900=matrix;
    save zdisp851_900.mat zdisp851_900;
    clear zdisp851_900; clear matrix;
case 19
    zdisp901_950=matrix;
    save zdisp901_950.mat zdisp901_950;
    clear zdisp901_950; clear matrix;
case 20
    zdisp951_999=matrix;
    save zdisp951_999.mat zdisp951_999;
    clear zdisp951_999; clear matrix;    
end
end
clear matrix; clear Coord; clear zdisp;
%%% Remainder left %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if y>0 & rem(n,50)>0
    disp('Reading data...');
    newfile=[file '/' d int2str(y*50+1)];
    fid=fopen(newfile,'r');
    B=fread(fid,S.NUMNP*3+21,precision);
    B=B(22:S.NUMNP*3+21);
    Coord=B;
    status = fclose(fid);
for i=2:rem(n,50)
    newfile=[file '/' d int2str(y*50+i)];
    fid=fopen(newfile,'r');
    B=fread(fid,S.NUMNP*3+21,precision);
    B=B(22:S.NUMNP*3+21);
    Coord=[Coord B];
    status = fclose(fid);
end
%Reading from the dyna file to find which nodes are used

newfile=[file '/' grant];
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
                                                                                                                            
                                                                                                                            
%Sorting data into the x,y,z components                                                                                     
disp('Sorting data...');
r=1:S.NUMNP;                                                                                                                
x_r=3*r'-2;
y_r=3*r'-1;                                                                                                                 
z_r=3*r';

x_orig=Coord(x_r,1);
y_orig=Coord(y_r,1);
z_orig=Coord(z_r,1);
x_value=Coord(x_r,1:rem(n,50));
y_value=Coord(y_r,1:rem(n,50));
z_value=Coord(z_r,1:rem(n,50));


%Creating 3D matrix
for w=1:rem(n,50)
    matrix(:,1,w)=node_loc(:,1);
end

for r=1:rem(n,50)
    matrix(:,2,r)=x_value(:,r)-x_orig;
    matrix(:,3,r)=y_value(:,r)-y_orig;
    matrix(:,4,r)=z_value(:,r)-z_orig;
end

%Creating default zdisp.mat file
zdisp_rem = matrix;
save zdisp_rem;
end
disp('File successfully created.');
