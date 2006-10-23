function []=viewlatoutput(dynfile,outfile,numaxnodes,numelenodes,ndspc)
%function []=viewlatoutput(dynfile,outfile,numaxnodes,numelenodes,ndspc)
% function to display the intensity profile along the center
% axial-lateral plane in the FEM models
% INPUTS:
% dynfile - ls-dyna input deck to read node coordinate info from
% outfile - output file that has node/force variable
% numaxnodes - # of axial nodes in mesh
% numelenodes - # of elevation nodes in mesh
% ndpsc - spacing of nodes (mm)
% OUTPUTS:
% None; figure is generated.
% Example: 
% viewoutput('grant.dyn','output0p5.asc',126,21,0.2)
% mark 07/23/03

[readnode]=read_dyna_nodes(dynfile);
index=1;
for i=1:length(readnode),
        if(readnode(i,3) < 0.01 & readnode(i,3) > -0.01)
                nodes(index)=readnode(i,1);
                node_coord(1,index)=readnode(i,2);
                node_coord(2,index)=readnode(i,3);
                node_coord(3,index)=readnode(i,4);
                index=index+1;
        end;
end;

disp('node and node coordinate matrices have been created!')

% sort everything out
[Y,I]=sort(node_coord(1,:));
nodes=nodes(I);
node_coord(1,:) = node_coord(1,I);
node_coord(3,:) = node_coord(3,I);

node_coord3=reshape(node_coord(3,:),numaxnodes,numelenodes);
nodefind = reshape(nodes,numaxnodes,numelenodes);

disp('sorting stuff out...')
for m=1:numaxnodes,
        [Z,N]=sort(node_coord3(m,:));
        nodefind(m,:)=nodefind(m,N);
end;

% read in the output*.asc file
% this will load in a 5 column variable, with the node ID being the 1st
% column, the second column being the degree of freedom (1-x, 2-y, 3-z), and 
% the 4th column being the force magnitude in that direction (dynes)
disp('reading in the output file...')
outvar=load(outfile);

disp('extracting axial force components')
for j=1:numaxnodes,
	for k = 1:numelenodes,
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
%for j = 1:numelenodes,
%	for k = 1:numlatnodes,
%		ah(j,k) = find(measurementPointsandNodes(:,1) == nodefind(j,k));
%		
%	end;
%end;
%inten=isptaout(ah);

figure
ax=(1:numaxnodes)*ndspc;
ele=(1:numelenodes)*ndspc;
%imagesc(lat,ax,inten)
imagesc(ele,ax,force)
colormap(gray)
colorbar
xlabel('Elevation Position (mm)')
ylabel('Axial Position (mm)')
