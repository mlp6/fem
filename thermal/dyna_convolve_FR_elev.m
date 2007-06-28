function []=dyna_convolve_FR(correction,tmax)
%function []=dyna_convolve_FR(correction,tmax)
%%%%%%%
% this is a modified version of dyna_convolve_FR.m that now extracts
% temperatures on the axial-elevation plane instead of the axial-lateral
% plane
% mark 11/12/03
%%%%%%%
%correction = 0.145;	% 10 ele
%correction = 1.0;	% 69 ele
%tmax - max t*.asc file to read in
% generate dyna_convolve_FR_elev file for convolveFR.m
%
% modified to read in dyna output from mutiple time steps
% mark 12/15/02
% correction - scale factor for using less elemenets (relative to 69)

NO_ELEV_NODES = 29;

%%%% code copied from Steve's read nodes script %%%%
fname = '/home/mlp6/arfi/arfi7.dyn'
endofline=sprintf('\n');

fid=fopen(fname,'r');
if (fid == -1),
        disp(['Can''t open ' fname]);
        return;
        end;
s=fscanf(fid,'%s',1);
while (~strcmp(s,'*NODE')),
        s=fscanf(fid,'%s',1);
        end;
c=fscanf(fid,'%c',1);
while(c~=endofline);
        c=fscanf(fid,'%c',1);
        end;
disp('reading in node data...')
[nodedata,count]=fscanf(fid,'%i %f %f %f',[4,inf]);
nodedata=nodedata';
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% find the nodes in the axial-elevation plane of the model
index=1;
for i=1:length(nodedata)
        if(nodedata(i,3) > -0.01 & nodedata(i,3) < 0.01) 
        nodes(index)=nodedata(i,1);
        node_coord(1,index)=nodedata(i,2);
        node_coord(2,index)=nodedata(i,3);
        node_coord(3,index)=nodedata(i,4);
        index=index+1;
        end;
end;
disp('node and node coordinate matrices created...')
fclose(fid);

% now, all of the data is read in... lets re-sort it into a plane
% sort the node IDs by y-coordinate
[Y,I]=sort(node_coord(1,:));
nodes=nodes(I);
node_coord(1,:) = node_coord(1,I);
node_coord(3,:) = node_coord(3,I);

% reshape the z-coordinates into a plane matrix, along with corresponding 
% node IDs
node_coord3=reshape(node_coord(3,:),107,NO_ELEV_NODES);
nodefind = reshape(nodes,107,NO_ELEV_NODES);

% now sort each column of the matrix to have ascending axial entries
for m=1:107,
	[Z,N]=sort(node_coord3(m,:));
	nodefind(m,:)=nodefind(m,N);
end;

% create temperature matrix
temps = zeros(107,NO_ELEV_NODES,tmax);

%%% CHANGED TO ACCOMODATE ADDITIONAL FRAMES %%%
for n=1:tmax,
	disp(n);
	filetemp=load(sprintf('t%i.asc',n));
	t(:,:)=filetemp;

	% now assign temperatures to the node IDs in the matrix
%	for i=1:107,
%		for j=1:71,
%			[slot]=find(t(:,1)==nodefind(i,j));
%			if(length(slot)~=0)
%				temps(i,j,n)=t(slot,2);
%			end;
%		end;
%	end;
%	for i=1:length(t(:,1)),
%		[slot1,slot2]=find(nodefind==t(i,1));
%		if(length(slot1)~=0)
%			temps(slot1,slot2,n)=t(i,2);
%		end;
%	end;

	T = zeros(220313,1);
	T(t(:,1))=t(:,2);
	temps(:,:,n)=T(nodefind);
	clear t;	
end;

clear T
% correction for using 10 instead of 69 elements
temps = temps*correction;

% lets plot the output
%lat = 1:71;
%lat = lat*0.035;
elev = 1:NO_ELEV_NODES;
elev = elev*0.035;
ax = 107:-1:1;
ax = ax*0.035;
figure
%colormap(gray)
imagesc(elev,ax,temps(:,:,1));
%title('Temperature Profile')
xlabel('Elevation Position (cm)')
ylabel('Axial Position (cm)')
colorbar;

eleva = 1:400; eleva = eleva*0.0175;

save dyna_convolve_FR_elev.mat temps elev eleva ax
