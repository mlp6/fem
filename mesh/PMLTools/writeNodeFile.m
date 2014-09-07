function writeNodeFile(nodeFile,nodes)
%Write node file based on given input file name and an Nx10 elements array
%
%
%Author: MRS
%Edit: CJM - OS Independence - 8/27/14
%Edit: CJM - Added dynamic sizing of nodes card based on number of
%constraints to be used in nodes. - 8/30/2014
% disp(nodeFile)
fid = fopen(nodeFile(2:end),'w');
fprintf(fid,'*NODE\n');

nodeFormat = '%d,%3.8f,%3.8f,%3.8f\n';
if(size(nodes,2)==5)
    nodeFormat = '%d,%3.8f,%3.8f,%3.8f,%d\n';
elseif(size(nodes,2)==6)
    nodeFormat = '%d,%3.8f,%3.8f,%3.8f,%d,%d\n';
end

for i=1:size(nodes,1)
     fprintf(fid,nodeFormat,nodes(i,:));
end

fprintf(fid,'*END\n');
fclose(fid);