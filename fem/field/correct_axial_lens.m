function lens_correction_m = correct_axial_lens(Th_data)
% function lens_correction_m = correct_axial_lens(Th_data)
% 
% INPUTS:   Th_data - array of values from Field II xdc_get(Th, 'rect')
%
% OUTPUTS:  lens_correction_m (float) - axial shift of the center of the center
%                                       element (m)

% find the center element of the array (x == 0)
center_ele_index = min(find(Th_data(8,:)>=0));

% find axial offset of the center of this center element
lens_correction_m = Th_data(10,center_ele_index);
