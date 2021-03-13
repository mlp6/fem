function probe = read_probe_json(probe_json_file);
% function probe = read_probe_json(probe_json_file);
%
% PARAMS:
%    probe_json_file (str) - JSON file path
%
% RETURNS:
%     probe (struct)
%

rawtext = fileread(probe_json_file);

if ~isrow(rawtext)
    rawtext = rawtext';
end

probe = jsondecode(rawtext);
