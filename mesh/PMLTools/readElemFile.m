function elemsOut = readElemFile(varargin)
%Read in an elements file with a given input file name string 
%
%Author MRS
%Update - CJM  Added adaptive header line reading 8/27/14   
%

if(nargin>0)
    elemsFile = varargin{1};
else
    elemsFile = 'elems.dyn';
end

fid = fopen(elemsFile,'r');

%find number of header lines
tline = fgetl(fid);
hl=0;
while(isempty(cell2mat(textscan(tline,'%d'))))
    tline = fgetl(fid);
    hl=hl+1;
end
frewind(fid); %back to beginning of file

elems = textscan(fid,'%d%d%d%d%d%d%d%d%d%d','CommentStyle','*','Delimiter',',','HeaderLines',hl);
fclose(fid);
elems = cell2mat(elems);

elemsOut = ones(max(elems(:,1)),size(elems,2)).*NaN;
elemsOut(elems(:,1),:) = elems;



