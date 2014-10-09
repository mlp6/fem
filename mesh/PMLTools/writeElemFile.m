function writeElemFile(elemsFile,elems)
%Write elements file based on given input file name and an Nx10 elements
%array
%
%Author MRS
%Edit CJM - OS Independence - 8/27/14

fid = fopen(elemsFile,'w+');
fprintf(fid,'*ELEMENT_SOLID\n');

for i=1:size(elems,1)
    fprintf(fid,'%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n',elems(i,:));
end

fprintf(fid,'*END\n');
fclose(fid);