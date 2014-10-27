function check_on_axis(measurementPoints)
% function check_on_axis(measurementPoints)
%
% check to see if nodes exist on the x = y = 0 plane to insure that the
% intensity fields are properly represented
%
xlocs = unique(measurementPoints(:,1));
ylocs = unique(measurementPoints(:,2));

% test for x and y locations that are at 0 (imaging plane), and if both don't
% exist, then display a warning
if((max(xlocs==0.0) + max(ylocs==0.0)) < 2),
    warning('There are not nodes in the lateral / elevation plane = 0 (imaging plane). This can lead to inaccurate representations of the intensity fields!!');
end
