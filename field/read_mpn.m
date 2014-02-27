function [mpn] = read_mpn(NodeName)
% 
% read nodes.dyn and extract points & nodes
%

% the node file will contain comment lines starting with '*' and '$', which
% creates a problem for lots of text parsers that are fast, but limited on
% ignoring things; we will use grep to exclude comment lines and then read in
% the data
pid = feature('getpid');
tmpNodeName = sprintf('%s.%s', NodeName, pid);
if exist(tmpNodeName, 'file');
    error(sprintf('ERROR: Temp node file for parsing already exists (%s)', tmpNodeName));
elseif ~exist(NodeName, 'file');
    error(sprintf('ERROR: %s does not exist', NodeName));
else
    % exclude lines starting with * or $
    disp('STATUS: removing comment / header lines with egrep');
    grep_cmd = sprintf('egrep -v ''(^\\*|^\\$)'' %s > %s', NodeName, tmpNodeName);
    disp(sprintf('STATUS: temp, comment-stripped, node def file created (%s)', tmpNodeName));
    system(grep_cmd);
end

% read in the nodes
try
    fid = fopen(tmpNodeName,'r');
catch exception
    error(sprintf('ERROR: %s does not exist', tmpNodeName));
end

% all comments have been removed, so we can go crazy with using simple, but
% fast, textscan
disp('STATUS: reading in node definitions');
tic
    mpn = textscan(fid, '%f%f%f%f', 'Delimiter', ',');
    disp('STATUS: done reading node definitions');
toc

fclose(fid);

try
    system(sprintf('rm %s', tmpNodeName));
    disp(sprintf('STATUS: temp node def file removed (%s)', tmpNodeName));
catch
    error(sprintf(sprintf('ERROR: Could not remove temp node def file (%s)', tmpNodeName)));
end

% textscan creates a huge cell
% convert this to array for use downstream
mpn = cell2mat(mpn);
