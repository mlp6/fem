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

switch probe.name
    case {'vf105', 'vf135', 'vf73', 'vf105gfp', 'sonivate', 'tu15l8w', 'l74', ...
          'l94', 'l124', 'l145', 'i7505', 'acunav64', 'acunav128', ...
          'acunav128_fullapp', 'er7bl', 'p42', 'ph41', 'pl35elegra'}
        Th = xdc_focused_multirow(probe.no_elements, probe.width,
                                  probe.no_elements_y, probe.height, ... 
                                  probe.kerf, probe.kerf, probe.Rfocus, ...
                                  probe.no_sub_x, probe.no_sub_y, ...
                                  FIELD_PARAMS.focus);
    case {'c52', 'c52v', 'ch41', 'ch62', 'ev94'}
        Th = xdc_convex_focused_array(probe.no_elements, probe.width, probe.height, ...
                                      probe.kerf, probe.Rconvex, probe.Rfocus, ...
                                      probe.no_sub_x, probe.no_sub_y, ...
                                      FIELD_PARAMS.focus);
    case {'hifu', 'drug_piston'}
        Th = xdc_concave(probe.R, probe.Rfocal, probe.ele_size);
    case {'v41c'}
        Th = xdc_focused_array(probe.no_elements, probe.width, probe.height, ...
                               probe.kerf, probe.Rfocus, probe.no_sub_x, ...
                               probe.no_sub_y, FIELD_PARAMS.focus);
    otherwise
        warning('Specified probe not explicitly handled.')
