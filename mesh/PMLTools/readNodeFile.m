function nodesOut = readNodeFile(varargin)
%Read in a node file with a given input file name string 
%
%Author MRS
%Update - CJM  Added adaptive header line reading 8/27/14    
%

if(nargin>0)
    nodeFile = varargin{1};
else
    nodeFile = 'nodes.dyn';
end

fid = fopen(nodeFile,'r');

%find number of header lines
tline = fgetl(fid);
hl=0;
while(isempty(cell2mat(textscan(tline,'%d'))))
    tline = fgetl(fid);
    hl=hl+1;
end

frewind(fid); %back to beginning of file

nodes = textscan(fid,'%f%f%f%f%f %*[^\n]','CommentStyle','*','Delimiter',',','HeaderLines',hl);  %only need first 4 numbers, skip the rest of the line

fclose(fid);
nodesOut = cell2mat(nodes);

scale = 1000; %Fix Roundoff Errors
for i=2:4,
    nodesOut(:,i) = nodesOut(:,i) * scale;
    nodesOut(:,i) = round(nodesOut(:,i));
    nodesOut(:,i) = nodesOut(:,i) / scale;
end;
