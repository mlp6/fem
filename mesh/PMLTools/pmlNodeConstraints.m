function pmlNodeConstraints(nodeFile,sym)
%Constrain all nodes that will be included in a PML. 
%
% INPUTS
%   nodeFile (str) - Input file name of node file
%   sym (str, 'q','h','n') - Symmetry condition, see below.
%
% OUTPUTS
%   outputs a node file with the same name as the input, adding _pml to the
%   file name.
%
%sym = 'q', 'h', or 'n'
% for q (quarter) symmetry, the x=0, and y=0 planes are the 2 planes of symmetry
%   the most negative x plane, and most positive y plane are fully
%   constrained
%   in this case we have to address the nodes on the x=0,y=0 axis as a
%   special case
% for h (half) symmetry, the x=0 plane is the plane of symmetry
%   the most negative x plane, and the most negative & most positive y planes are fully
%   constrained
% for n (no) symmetry
%   the most negative & most positive x plane, and the most negative & most positive y planes are fully
%   constrained
%
% in all cases the bottom (most negative) z plane is fully constrained
%
% Author: MRS - 04/10/2014
% Edit: CJM - Added notes, comments and cleanup code - 08/27/2014 

nodes=readNodeFile(nodeFile);
nodes(:,5)=0;

%define node planes
xminPlane=nodes(:,2)==min(nodes(:,2));
yminPlane=nodes(:,3)==min(nodes(:,3));
xmaxPlane=nodes(:,2)==max(nodes(:,2));
ymaxPlane=nodes(:,3)==max(nodes(:,3));
zminPlane=nodes(:,4)==min(nodes(:,4));
zmaxPlane=nodes(:,4)==max(nodes(:,4));

%define values for node planes
switch sym
    case 'q'
        xmaxPlaneNodes=1;
        yminPlaneNodes=2;
    case 'h'
        xmaxPlaneNodes=1;
        yminPlaneNodes=7;
    case 'n'
        xmaxPlaneNodes=7;
        yminPlaneNodes=7;
end
 
%same in all cases
xminPlaneNodes=7;
ymaxPlaneNodes=7;
zminPlaneNodes=7;
zmaxPlaneNodes=7; %added plm on top too

%set card 5 for nodes on each respective plane to appropriate value
axes = ['x','y'];
vals = {'min','max'};
for i=1:length(axes)
    for j=1:length(vals)
        thisPlane = sprintf('%s%s',axes(i),vals{j});
        eval(sprintf('nodes(%sPlane,5)=%sPlaneNodes;',thisPlane,thisPlane))
    end
end

if(sym=='q')
    nodes(intersect(find(xmaxPlane),find(yminPlane)),5)=4;  %x=0,y=0 axis
end

axes = 'z';
vals = {'min','max'};
for i=1:length(axes)
    for j=1:length(vals)
        thisPlane = sprintf('%s%s',axes(i),vals{j});
        eval(sprintf('nodes(%sPlane,5)=%sPlaneNodes;',thisPlane,thisPlane))
    end
end

[pathstr,name,ext] = fileparts(nodeFile);
newNodeName = sprintf('%s%s%s_pml%s',pathstr,filesep,name,ext);
writeNodeFile(newNodeName,nodes)

end


