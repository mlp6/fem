function []=dyna_convolve(correction)
%function []=dyna_convolve(correction)
% correction= 1.0 (69 ele) 0.145 (10 ele)
%
% script to convolve thermal field for a single ARFI sequence
% and convolve it with sequential lateral pushes
% mark 11/13/02
% 
% modified to read in dyna output and conolve data from mutiple time
% steps
% mark 12/15/02
% correction - scale factor for using less than 69 elements

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
% find the nodes on the back plane of the model
index=1;
for i=1:length(nodedata)
        if(nodedata(i,2) == 0.0) 
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
[Y,I]=sort(node_coord(2,:));
nodes=nodes(I);
node_coord(2,:) = node_coord(2,I);
node_coord(3,:) = node_coord(3,I);
%node_coord(3,:) = node_coord(3,:);

% reshape the z-coordinates into a plane matrix, along with corresponding 
% node IDs
node_coord3=reshape(node_coord(3,:),107,71);
nodefind = reshape(nodes,107,71);

% now sort each column of the matrix to have ascending axial entries
for m=1:107,
	[Z,N]=sort(node_coord3(m,:));
	nodefind(m,:)=nodefind(m,N);
end;

% create temperature matrix
temps = zeros(107,71,2000);

for n=1:2000,
	disp(n);
	filetemp=load(sprintf('t%i.asc',n));
	t(:,:,n)=filetemp;

	% now assign temperatures to the node IDs in the matrix
%	for i=1:107,
%		for j=1:71,
%			[slot]=find(t(:,1,n)==nodefind(i,j));
%			if(length(slot)~=0)
%				temps(i,j,n)=t(slot,2,n);
%			end;
%		end;
%	end;
%	for i=1:length(t(:,1,n)),
%		[slot1,slot2]=find(nodefind==t(i,1,n));
%		if(length(slot1)~=0)
%			temps(slot1,slot2,n)=t(i,2,n);
%		end;
%	end;

	T = zeros(220313,1);
	T(t(:,1,n))=t(:,2,n);
	temps(:,:,n)=T(nodefind);

end;

clear T
temps=temps*correction;

% lets plot the output
lat = 1:71;
lat = lat*0.035;
ax = 107:-1:1;
ax = ax*0.035;
%figure
%colormap(gray)
%imagesc(lat,ax,temps(:,:,5));
%title('Temperature Profile')
%xlabel('Laterial Position (cm)')
%ylabel('Axial Position (cm)')
%colorbar;

% now lets move the thermal field over for an adjacent ARFI sequence
% assuming that lateral spacing is 0.047*4 = 0.188mm

% need finer sampling than dyna's element width of 0.035cm... so will 1/2
% lateral spacing (0.175mm)
%arfitemp = zeros(107,400,no_lines);
%for n=1:no_lines,
%	arfitemp(:,(1+n):2:(141+n),n) = temps(:,:,n);
%	arfitemp(:,(2+n):2:(142+n),n) = temps(:,:,n);
%end;

% sum it all up!
%arfi_convolve =zeros(107,400);
%for b=1:no_lines,
%	arfi_convolve = arfi_convolve(:,:) + arfitemp(:,:,b);
%end;

%figure
%lata = 1:400; lata = lata*0.0175;
%colormap(gray)
%imagesc(lata,ax,arfi_convolve)
%%title('Convolved ARFI Image')
%xlabel('Lateral Position (cm)')
%ylabel('Axial Position (cm)')
%colorbar

%disp('max temp...'); disp(max(max(arfi_convolve)));
save dyna_convolve.mat temps lat lata ax
