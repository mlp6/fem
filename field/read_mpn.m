function [mpn] = read_mpn(NodeName)
% 
% read nodes.dyn and extract points & nodes
%

% read in the nodes
try
    fid = fopen(NodeName,'r');
catch exception
    error(sprintf('%s does not exist',NodeName));
end

% preallocate the mpn matrix to avoid a massive memory frag problem with
% dynamic allocation w/ each line read
% read number of lines, including comments
[e, numLines] = system(sprintf('wc -l %s | awk ''{print $1}''', NodeName));
mpn = zeros(str2num(numLines),4);

nodecount = 0;
templine = fgetl(fid);
while ischar(templine)
    % check for comment line delimiters at start of line, and only parse data
    % if they do not exist
    comment_test = logical(regexp(templine,'^(\*|\$)'));
    if comment_test
        disp('Skipping comment line... ')
    else
        nodecount = nodecount + 1;
        val = regsplitcell(templine);
        mpn(nodecount,:) = val';
    end
    templine = fgetl(fid);
end

disp('Done reading node definitions.')
fclose(fid);

% remove extra entries in mpn that were extracted comments
mpn = mpn(1:nodecount,:);

% test to see if the node definition matrix is the correct / expected size
if (size(mpn,2) ~= 4 || size(mpn,1) ~= nodecount),
    error('ERROR: mpn matrix has inconsistent dimensions (%i x %i vs %i x %i)', size(mpn, 1), ...
                                                                                size(mpn, 2), ... 
                                                                                nodecount, ...
                                                                                4);
else
    disp('Node positions successfully extracted.')
end
end


function [nodeval] = regsplitcell(templine)
val = regexp(templine, ',', 'split');
valstr = str2mat(val);
nodeval = str2num(valstr);
end
