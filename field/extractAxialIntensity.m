function [axial,intensity]=extractAxialIntensity(InputName,NormName,IsppaNorm);
% function [axial,intensity]=extractAxialIntensity(InputName,NormName,IsppaNorm);
%
% INPUTS:
% InputName (string) - dyna*.mat file to process
% NormName (string) - dyna*.mat file with known Isppa 
% IsppaNorm (float) - Isppa value for the normalization file (W/cm^2)
% 
% OUTPUTS:
%   axial (float vector) - axial positions (mm)
%   intensity (float vector) - intensities along axial
%
% Example:
% makeLoadsTemps('dyna_ispta_att0.5.mat','/emfd/mlp6/field/VF10-5/
% F1p3_foc20mm/dyna_ispta_att0.5.mat',5357);
%
% Mark Palmeri (mlp6)
% 2011-10-27
 
% node tolerance to search for center line in the lateral
% dimension
LatTol = 1e-3;  % cm

% find the Isppa value that Field II solved for in the
% normalization case (limiting the search to the focal zone,
% +/- 25% the focal depth)
AxialSearch = 0.25; % percentage of the focal depth to search
										%for the Isppa value
load(NormName);
NormIntensity = intensity;
mpn = FIELD_PARAMS.measurementPointsandNodes;
NormFocalDepth = FIELD_PARAMS.focus(3)*100;  % convert m -> cm

% check to make sure nodes exist at lat == 0 for the push
if(isempty(find(abs(mpn(:,3)) < LatTol))),
    error('lat = 0 nodes missing for rad force excitation');
end;

NormFZ=find(abs(mpn(:,2)) < 5e-6 & abs(mpn(:,3))<LatTol & abs(mpn(:,4)) > (NormFocalDepth - NormFocalDepth*AxialSearch) & abs(mpn(:,4)) < (NormFocalDepth + NormFocalDepth*AxialSearch)); 

% what is the Isppa value that field has solved
NormFieldIsppa = max(NormIntensity(NormFZ))

% find normalization max in desired alpha
load(InputName);
InputIntensity = intensity;
mpn = FIELD_PARAMS.measurementPointsandNodes;
FocalDepth = FIELD_PARAMS.focus(3)*100;  % convert m -> cm

FZ=find(abs(mpn(:,2)) < 5e-6 & abs(mpn(:,3))<LatTol & abs(mpn(:,4)) > (FocalDepth - FocalDepth*AxialSearch) & abs(mpn(:,4)) < (FocalDepth + FocalDepth*AxialSearch)); 

% what is the Isppa value that field has solved
FieldIsppa = max(InputIntensity(FZ))

% normalize InputIntensity
InputIntensity = InputIntensity./FieldIsppa;

% toss intensities below 5% of Isppa
InputIntensity=InputIntensity.*(InputIntensity>=0.05);

% now zero out values near the transducer face b/c they
% violated the farfield assumption in field
z0=find(abs(mpn(:,4)) < 0.001);
InputIntensity(z0)=0;

% the BIG step - scale the Field intensities relative to the
% known intensity value for the normalization data
Field_I_Ratio = FieldIsppa/NormFieldIsppa
ScaledIntensity=InputIntensity*IsppaNorm*Field_I_Ratio;

axial = abs(mpn(FZ,4)) * 10;
intensity = ScaledIntensity(FZ);
