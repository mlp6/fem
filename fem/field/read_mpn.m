function [mpn] = read_mpn(NodeName)
% function [mpn] = read_mpn(NodeName)
% 
% Read nodes.dyn and extract points & nodes, skipping the header lines,
% including *NODE, and ending when the 4 column fscanf is broken (by *END).
%
% INPUTS:   NodeName ('nodes.dyn')
%
% OUPUTS:   mpn (array of nodeID, x, y, z coords)
%
% Mark Palmeri
% mlp6@duke.edu

try
    fid = fopen(NodeName, 'r');
catch
    error(sprintf('ERROR: %s does not exist', NodeName));
end

endofline = sprintf('\n');
  
s = fscanf(fid, '%s', 1);
while (~strcmp(s, '*NODE')),
    s = fscanf(fid, '%s', 1);
end

c = fscanf(fid, '%c', 1);
while(c ~= endofline);
    c = fscanf(fid, '%c', 1);
end

[mpn] = fscanf(fid, '%d,%f,%f,%f', [4, inf]);

fclose(fid);

mpn = mpn';
