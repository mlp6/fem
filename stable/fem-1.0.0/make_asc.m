function make_asc(input_filename,normalize_fname,output_filename,thr,alpha,nodespc,focus);
%function make_asc(input_filename,normalize_fname,output_filename,thr,alpha,nodespc,focus);
% - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
% MODIFICATION HISTORY
% Added print statements for *LOAD_NODE_POINT and *END to the
% head and tail of the output file respectively to be directly
% included in the the dyna input decks using a *INCLUDE
% keyword
% Mark 03/26/05
%
% Changing element volume for new arfi8 model
% Mark 02/14/03
%
% Modified to make sure that all of the pushes are in the correct
% direction
% Mark 10/24/02
%
% Limiting force application to w/i physical dimensions of the transducer
% Mark 09/19/02
%
% Adding directional components to the force so that not all of the pushing is 
% in the z-direction
% Mark 09/17/02
%
% CORRECTED FOR NEAR-FIELD APPROX; NO FORCE ON Z=0 NODES
% Mark 09/12/02
% - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
% DESCRIPTION
% this script writes a output_filename.asc file based on the intensities
% supplied by input_filename
% 
% node forces are determined by calculating a scale factor based on, 
% an empirically derived body force for a=0.5dB/cm/MHz, and lumping that into
% a point load for an element volume
% - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

% calculate volume of an element
vol = (nodespc)^3; % cm^3

% the following value was obtained using (2 alpha I) / c
% assuming alpha=0.5 (our 'reference' absorption).
refpeakforceval=54000; % g/cm^2 s^2 (54 kg/cm^2 s^2) for alpha=0.5
alphanorm=0.5;
% g/cm^2 s^2, scaled for desired alpha 
peakforceval=refpeakforceval*alpha/alphanorm; 
scale=vol*peakforceval;

% now need to scale for Isppa vs Ispta
% 900 - 0.9ms that Ispta was calculated
% 28*6 - number of microseconds that pulses are applied for 
scale = scale*900/(28*6);

% find normalization value from alpha=0.5 db output
% by looking only along center axial line; this max will be at
% the focal depth, which is where the emperically-measured
% Ispta was measured
load(normalize_fname);
i=find(abs(measurementPointsandNodes(:,2))<3e-6 & abs(measurementPointsandNodes(:,3))<0.03 & abs(measurementPointsandNodes(:,4))>nodespc);
normvala=max(isptaout(i))

% changed the search below to just use the same index as the
% normalized file since that should be the same for scaling
load(input_filename);
%ii=find(abs(measurementPointsandNodes(:,2))<3e-6 & abs(measurementPointsandNodes(:,3))<0.03 & abs(measurementPointsandNodes(:,4))>nodespc);
%plot(measurementPointsandNodes(ii,4),isptaout(ii))
%normvalb=max(isptaout(ii))
normvalb=max(isptaout(i))
isptaout=isptaout/normvalb;

% threshold below thr
isptaout=isptaout.*(isptaout>=thr);

% now divide the magnitude by 2 on the plane of symmetry (x=0)
i=find(measurementPointsandNodes(:,2)<3e-6);
isptaout(i)=isptaout(i)/2;

% now zero out z=0 values b/c they violated the farfield
% assumption in field and aren't valid ispta values
i=find(abs(measurementPointsandNodes(:,4))<0.02);
isptaout(i)=0;

% now scale to value of reference alpha
scalefactor=normvalb/normvala
isptaout=isptaout*scalefactor; 

% write forces to *.asc file
% open the file and add *LOAD_NODE_POINT to the head
fid=fopen(output_filename,'w');
fprintf(fid,'*LOAD_NODE_POINT\n');

for x=1:length(measurementPointsandNodes),
	% compute some variables to determine the direction the force should be
	% applied in (x,y,z)
	% mark 09/17/02
	xcoord = measurementPointsandNodes(x,2);
	ycoord = measurementPointsandNodes(x,3);
	zcoord = measurementPointsandNodes(x,4);
	% focal zone offset to just apply force in axial direction
	% will use 10% of focal depth (cm)
	foc = focus(3)*100;
	axoff = foc*0.05;
	if(zcoord>=(-foc+axoff)),
		magnitude = sqrt(xcoord^2 + ycoord^2+((foc+zcoord)^2));
		if(magnitude==0),
			xscale=0;
			yscale=0;
			zscale=-1;
		else
			xscale = -xcoord/magnitude;
			yscale = -ycoord/magnitude;
			zscale = (-foc-zcoord)/magnitude;
		end;
	elseif(zcoord<(-foc+axoff) & zcoord>(-foc-axoff))
                 xscale=0;
		 yscale=0;
                 zscale=-1;
	elseif(zcoord<(-foc-axoff))
		magnitude = sqrt(xcoord^2 + ycoord^2+((foc+zcoord)^2));
		if(magnitude==0),
			xscale=0;
			yscale=0;
			zscale=-1;
		else
			xscale = xcoord/magnitude;
			yscale = -ycoord/magnitude;
			zscale = (foc+zcoord)/magnitude;
		end;
	else
		%disp('something is not correct in defining the force direction')
	end;
	% we don't want any force applied to the near-field nodes (z=0)
	% or outside the x-ducer dimensions
	% mark 09/19/02
	if (isptaout(x)*scale>1e-8 & abs(zcoord)>0.02 & abs(xcoord)<0.25 &...
	 abs(ycoord)<0.75) 
%		fprintf(fid,'%d,1,1,%0.2e,0 \n',measurementPointsandNodes(x,1),xscale*isptaout(x)*scale);
%		fprintf(fid,'%d,2,1,%0.2e,0 \n',measurementPointsandNodes(x,1),yscale*isptaout(x)*scale);
		fprintf(fid,'%d,3,1,%0.2e,0 \n',measurementPointsandNodes(x,1),zscale*isptaout(x)*scale);
	end;
end;

% add #END to tail of file and close the file ID
fprintf(fid,'*END\n');
fclose(fid);
