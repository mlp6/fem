function probe = read_probe_json(probe_json_file);
% function probe = read_probe_json(probe_json_file);
%
% PARAMS:
%    probe_json_file (str) - JSON file path
%
% RETURNS:
%     probe (struct)
%

fid = fopen(probe_json_file);
rawtext = fread(fid, '*char');
fclose(fid);

probe = jsondecode(rawtext);
