function Th = genTh(probe, FIELD_PARAMS)
% function Th = genTh(probe, FIELD_PARAMS)
%
% Generate Th Field II probe transducer definition based on the parameters in
% the probe struct.
%
% PARAMS:
%     probe (struct)
%     FIELD_PARAMS (struct)
%
% RETURNS:
%     Th - pointer to Field II transducer definition
%

switch probe.transducerType
    case 'focused_multirow'
        Th = xdc_focused_multirow(probe.noElements, probe.width, ...
                                  probe.noElementsY, probe.height, ... 
                                  probe.kerf, probe.kerf, probe.Rfocus, ...
                                  probe.noSubX, probe.noSubY, ...
                                  FIELD_PARAMS.focus_m');
    case 'convex_focused_array'
        Th = xdc_convex_focused_array(probe.noElements, probe.width, probe.height, ...
                                      probe.kerf, probe.Rconvex, probe.Rfocus, ...
                                      probe.noSubX, probe.noSubY, ...
                                      FIELD_PARAMS.focus_m');
    case 'concave'
        %case {'hifu', 'drug_piston'}
        Th = xdc_concave(probe.R, probe.Rfocal, probe.ele_size);
    case 'focused_array'
        %case {'v41c'}
        Th = xdc_focused_array(probe.noElements, probe.width, probe.height, ...
                               probe.kerf, probe.Rfocus, probe.noSubX, ...
                               probe.noSubY, FIELD_PARAMS.focus_m');
    otherwise
        warning('Specified probe type not explicitly handled.')
end
