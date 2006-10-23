function []=viewoutput(dynfile,outfile,numaxnodes,numlatnodes,ndspc)
%function []=viewoutput(dynfile,outfile,numaxnodes,numlatnodes,ndspc)
% function to display the intensity profile along the center
% axial-lateral plane in the FEM models
% INPUTS:
% dynfile - ls-dyna input deck to read node coordinate info from
% outfile - output file that has node/force variable
% numaxnodes - # of axial nodes in mesh
% numlatnodes - # of lateral nodes in mesh
% ndpsc - spacing of nodes (mm)
% OUTPUTS:
% None; figure is generated.
% Example: 
% viewoutput('grant.dyn','output0p5.asc',126,107,0.2)
% mark 07/23/03

[readnode]=read_dyna_nodes(dynfile);
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

disp('node and node coordinate matrices have been created!')

% sort everything out
[Y,I]=sort(node_coord(2,:));
nodes=nodes(I);
node_coord(2,:) = node_coord(2,I);
node_coord(3,:) = node_coord(3,I);

node_coord3=reshape(node_coord(3,:),numaxnodes,numlatnodes);
nodefind = reshape(nodes,numaxnodes,numlatnodes);

disp('sorting stuff out...')
for m=1:numaxnodes,
        [Z,N]=sort(node_coord3(m,:));
        nodefind(m,:)=nodefind(m,N);
end;

% save the center plane (sorted) for future use
save nodefind.mat nodefind

% read in the output*.asc file
% this will load in a 5 column variable, with the node ID being the 1st
% column, the second column being the degree of freedom (1-x, 2-y, 3-z), and 
% the 4th column being the force magnitude in that direction (dynes)
disp('reading in the output file...')
outvar=load(outfile);

disp('extracting axial force components')
for j=1:numaxnodes,
	for k = 1:numlatnodes,
		tempind = find(nodefind(j,k) == outvar(:,1) & outvar(:,2)==3) ;
		if(length(tempind) == 1),
			force(j,k) = tempind;
		elseif(length(tempind) == 0) 
			force(j,k) = 0;
		else
			error('ERROR!  multiple node/force association!!')
		end;
	end;
end;

%load(matfile)
% adjust for fact that node index does not correspond to the node ID
%disp('fixing node index/ID offsets...')
%for j = 1:numaxnodes,
%	for k = 1:numlatnodes,
%		ah(j,k) = find(measurementPointsandNodes(:,1) == nodefind(j,k));
%		
%	end;
%end;
%inten=isptaout(ah);

figure
ax=(1:numaxnodes)*ndspc;
lat=(1:numlatnodes)*ndspc;
%imagesc(lat,ax,inten)
imagesc(lat,ax,force)
colormap(gray)
colorbar
xlabel('Lateral Position (mm)')
ylabel('Axial Position (mm)')

figure
plot(ax,force(:,(numlatnodes/2)+0.5))
title('Axial Profile (Center)')
xlabel('Axial Position (mm)')
