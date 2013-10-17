function [axis,inten]=extractAxisIntensity(InputName,axis,location,Tol);
% function [axis,inten]=extractAxisIntensity(InputName,axis,location,Tol);
%
% INPUTS:
% InputName (string) - dyna*.mat file to process
% axis (int) - 1-3, based on dyna coordinates [1 = elevation, 2 = lateral, 3 = axial]
% location (floats) - 2 element vector with locations of the orthogonal positions (dyna units, cm)
% tol (float) - optional node search tolerance (dyna units, cm)
% 
% OUTPUTS:
%   axis (float vector) - axis positions (cm)
%   intensity (float vector) - intensities along axis
%
% EXAMPLE: [axial,intensity]=extractAxisIntensity('dyna.mat',3,[0 0])
%
% Mark Palmeri 
% mlp6@duke.edu
% 2013-10-16
 
% define node tolerance to search for axis line if not input specified
if(nargin < 4),
    Tol = 1e-3;
end;

in = load(InputName);
InputIntensity = in.intensity;
mpn = in.FIELD_PARAMS.measurementPointsandNodes;

axis = axis + 1; % first index is node ID, then x, y, z (2-4)
SearchDims = setdiff([2:4],axis);
axisOfInterest=find(abs(mpn(:,SearchDims(1))) < (location(1) + Tol) & ...
    abs(mpn(:,SearchDims(1))) > (location(1) - Tol) & ...
    abs(mpn(:,SearchDims(2))) < (location(2) + Tol) & ...
    abs(mpn(:,SearchDims(2))) > (location(2) - Tol));

axis = abs(mpn(axisOfInterest,axis));
inten = InputIntensity(axisOfInterest);
