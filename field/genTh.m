function Th = genTh(probe)
% function Th = genTh(probe)
%
% Generate Th Field II probe transducer definition based on the parameters in
% the probe struct.
%
% PARAMS:
%     probe (struct)
%
% RETURNS:
%     Th - pointer to Field II transducer definition
%

switch probe.type
    case 'focused_multirow'
        Th = xdc_focused_multirow(probe.no_elements, probe.width,
                                  probe.no_elements_y, probe.height, ... 
                                  probe.kerf, probe.kerf, probe.Rfocus, ...
                                  probe.no_sub_x, probe.no_sub_y, ...
                                  FIELD_PARAMS.focus);
    case 'convex_focused_array'
        Th = xdc_convex_focused_array(probe.no_elements, probe.width, probe.height, ...
                                      probe.kerf, probe.Rconvex, probe.Rfocus, ...
                                      probe.no_sub_x, probe.no_sub_y, ...
                                      FIELD_PARAMS.focus);
    case 'concave'
        %case {'hifu', 'drug_piston'}
        Th = xdc_concave(probe.R, probe.Rfocal, probe.ele_size);
    case 'focused_array'
        %case {'v41c'}
        Th = xdc_focused_array(probe.no_elements, probe.width, probe.height, ...
                               probe.kerf, probe.Rfocus, probe.no_sub_x, ...
                               probe.no_sub_y, FIELD_PARAMS.focus);
    otherwise
        warning('Specified probe type not explicitly handled.')
