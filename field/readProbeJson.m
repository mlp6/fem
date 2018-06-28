function probe = ReadProbeJson(probe_path, xdcr);
% function probe = ReadProbeJson(probe_path, xdcr);
%
% PARAMS:
%     probe_path (str): path to the probes repository with the JSON parameter files
%     xdcr (str): transducer name (without the .json filename extension)
%
% RETURNS:
%     probe (struct)
%

fid = fopen(strcat(probe_path, xdcr, '.json'));
rawtext = fread(fid, '*char');
fclose(fid);

probe = jsondecode(rawtext);
