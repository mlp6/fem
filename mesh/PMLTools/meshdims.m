function [nx ny nz]=meshdims(xdim,ydim,zdim,size)
%Function for determining # Divisions per dimension and proper orientation 
%to align with Mark's upside down right hand rule
%
%
%quarter symmetry x (elevational) dimension in cm
%quarter symmetry y (lateral) dimension in cm
%quarter symmetry z (axial) dimension in cm
%
%size - element size in microns 
%
%nx - number of divisions for x
%ny - number of divisions for y
%nz - number of divisions for z
%
% Author CJM - 8/27/2014
%
clc;

size=size/1E4;

nx=xdim/size;
ny=ydim/size;
nz=zdim/size;

xdim2=ceil(nx)*size;
ydim2=ceil(ny)*size;
zdim2=ceil(nz)*size;
if (xdim2==xdim && ydim2==ydim && zdim2==zdim)
display(sprintf('%s %d %s %0.3f %s','x should range(',0,',',-1*xdim2,'   )'));

display(sprintf('%s %d %s %0.3f %s','y should range(',0,',',ydim2,'    )'));

display(sprintf('%s %d %s %0.3f %s','z should range(',-0.1,',',-1*(zdim2+0.1),')'));

else
    display('In order to achieve this particular element size your mesh must be resized.');
    display('Please use the following values:');
    display(' ');
display(sprintf('%s %d %s %0.5f %s','x should range(',0,',',-1*xdim2,'   )'));

display(sprintf('%s %d %s %0.5f %s','y should range(',0,',',ydim2,'    )'));

display(sprintf('%s %0.1f %s %0.5f %s','z should range(',-0.1,',',-1*(zdim2+0.1),')'));
end
display(' ')
display(sprintf('%s %0.0d %s','The X dimension should have',ceil(nx),' divisions'));
display(sprintf('%s %0.0d %s','The Y dimension should have',ceil(ny),' divisions'));
display(sprintf('%s %0.0d %s','The Z dimension should have',ceil(nz),' divisions'));
display(' ')
display(sprintf('%s %0.4f %s','The element volume is (',nthroot((xdim2/ceil(nx))*(ydim2/ceil(ny))*(zdim2/ceil(nz)),3),'^3) cm^3'));
end
