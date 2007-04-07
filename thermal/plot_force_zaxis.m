function plot_force_zaxis(input_filename, normalize_fname, alpha, key);
%function plot_force_zaxis(input_filename, normalize_fname, alpha, key);
%
%
% plots inputfile z-axis after normalizing the force values w/r
% to  normalize_fname peak value on axis (i.e. 0.5 db/cm/MHz focus at 20)
% uses alpha to compute force, and key for plot linespec
% 
% forces are multiplied by scale, and by the volume of a cube
% that was determined from getting the coords of each node in 
% an element and computing the volume:
% this is a first pass....
%   [w l h] = 0.0379    0.0379    0.0379
%   vol = 5.4349e-05 cm^3
%
vol = 5.4349e-05; % cm^3
% once we multiply our value times volume and refpeakforceval, 
% our units for force are dynes (g cm/s^2)
%
%
% the following value was obtained using (2 alpha I) / c
% assuming alpha=0.5 (our 'reference' absorption.  So,
% it must be scaled by the alpha run for field...
refpeakforceval=54000; % g/cm^2 s^2 (54 kg/cm^2 s^2) for alpha=0.5
alphanorm=0.5;
peakforceval=refpeakforceval*alpha/alphanorm; % g/cm^2 s^2, scaled for desired alpha 
scale=vol*peakforceval;
% find normalization value from alpha=0.5 db output
% by looking only along center axial line
load(normalize_fname);
i=find(abs(measurementPointsandNodes(:,2))<3e-6 & abs(measurementPointsandNodes(:,3))<3e-6);
normvala=max(isptaout(i))

load(input_filename);
ii=find(abs(measurementPointsandNodes(:,2))<3e-6 & abs(measurementPointsandNodes(:,3))<3e-6);
normvalb=max(isptaout(ii))
isptaout=isptaout/normvalb;
%isptaout=isptaout.*(isptaout>=thr);% threshold below thr
%isptaout=isptaout.*(isptaout<1.01); % get rid of outliers

% now scale to value of reference alpha
scalefactor=normvalb/normvala
isptaout=isptaout*scalefactor*scale; 


plot(-measurementPointsandNodes(ii,4)*10,isptaout(ii),key)

