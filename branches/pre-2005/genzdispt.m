function []=genzdispt(fname,imax)
%function []=genzdispt(fname,imax)
% fname - *.dyn file to read node data from 
% imax - max index of *.asc file to read in
% read in *.asc files from ls-post and save result data to a *.mat file 
% for future matlab processing (trying to save disk space)
% mark 01/31/03

[readnode]=read_dyna_nodes(fname);
index=1;
for i=1:length(readnode),
	if(readnode(i,2) == 0.0)
		nodes(index)=readnode(i,1);
		node_coord(1,index)=readnode(i,2);
		node_coord(2,index)=readnode(i,3);
		node_coord(3,index)=readnode(i,4);
		index=index+1;
	end;
end;	

disp('node and node coordinate matrices created')

% sort everything out
[Y,I]=sort(node_coord(2,:));
nodes=nodes(I);
node_coord(2,:) = node_coord(2,I);
node_coord(3,:) = node_coord(3,I);

% reshape the z-coordinates into a plane matrix, along with corresponding 
% node IDs
% changed for arfi8 model
%node_coord3=reshape(node_coord(3,:),107,71);
%nodefind = reshape(nodes,107,71);
node_coord3=reshape(node_coord(3,:),121,141);
nodefind = reshape(nodes,121,141);

% now sort each column of the matrix to have ascending axial entries
%for m=1:107,
for m=1:121,
        [Z,N]=sort(node_coord3(m,:));
        nodefind(m,:)=nodefind(m,N);
end;

for i=1:imax,
	fname=sprintf('node_disp_t%i.asc',i);
	[zdisp]=grab_zdisp(fname,nodes);
	zdispt(i,:)=zdisp;
	disp(i)
end;
zdispt=-zdispt*1e4;
t=1:1:100;
t=t*1e-1;

save zdispt.mat zdispt t node_coords nodes
disp('zdisp.mat file created')
