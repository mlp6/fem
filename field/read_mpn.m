function [mpn] = read_mpn(NodeName, HeaderLinesToSkip)
% function [mpn] = read_mpn(NodeName, HeaderLinesToSkip)
% 
% Read nodes.dyn and extract points & nodes, skipping the first HeaderLinesToSkip lines, which includes *NODE
%
% INPUTS:   NodeName ('nodes.dyn')
%           HeaderLinesToSkip (4)
%
% OUPUTS: mpn (array of nodeID, x, y, z coords)
%
% Mark Palmeri
% mlp6@duke.edu
% 2014-07-01

try
    fid = fopen(NodeName,'r');
catch
    error(sprintf('ERROR: %s does not exist', NodeName));
end

mpn = textscan(fid, '%f%f%f%f', 'Delimiter', ',', 'HeaderLines', HeaderLinesToSkip);
mpn = cell2mat(mpn);

fclose(fid);