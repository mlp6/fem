function check_add_probes(probesPath)
% function check_add_probes(probesPath)
if exist(probesPath),
    addpath(probesPath);
else,
    warning('Probe definitions do not exist; must create your own');
end;
