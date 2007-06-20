function [lesion_nodes,coords]=create_lesion(center,radius);
% function [lesion_nodes,coords]=create_lesion(center,radius)
% center = [x y z] <- remember negative coordinates!!
% radius in cm
% this script will determine which elements are within a given radius
% of a defined center node, and find the associated elements with those nodes
% spit out results into lesion.asc
% Mark 09/30/02
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% optimized the element search function below
% Mark 05/14/04
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% added comments and some disp feedback;
% corrected the element search to use the size of the element
% matrix, not the node matrix
% Mark 01/25/05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% read in the node data from dyna deck
measurementPointsandNodes = read_dyna_nodes('/home/mlp6/arfi/cirs_nodes.dyn');

index=1;
for i=1:length(measurementPointsandNodes),
  %disp(sprintf('Computing %i node of %i.',i,length(measurementPointsandNodes)));
  xcoord = measurementPointsandNodes(i,2);
  ycoord = measurementPointsandNodes(i,3);
  zcoord = measurementPointsandNodes(i,4);
  radius_node = sqrt((xcoord-center(1))^2 + (ycoord-center(2))^2 + (zcoord-center(3))^2);
  rn(i) = radius_node;
  if(radius_node < radius)
    lesion_nodes(index) = measurementPointsandNodes(i,1);
    coords(index,1)=measurementPointsandNodes(i,2);
    coords(index,2)=measurementPointsandNodes(i,3);
    coords(index,3)=measurementPointsandNodes(i,4);
    index=index+1;
    disp('I found a node in the sphere!');
  end;
end;

% what is the size of lesion_nodes?
whos lesion_nodes

% define the end-of-line character
endofline=sprintf('\n');
  
% Open file
fid=fopen('/home/mlp6/arfi/cirs_elems.dyn','r');
if (fid == -1),
  disp(['Can''t open ' fname]);
  return;
end;

% find last word just before data... 
s=fscanf(fid,'%s',1);
while (~strcmp(s,'*ELEMENT_SOLID')),
  s=fscanf(fid,'%s',1);
end;

% Find start of next line...        
c=fscanf(fid,'%c',1);
while(c~=endofline);
  c=fscanf(fid,'%c',1);
end;
% Suck in data...  
% this needs to be changed based on whether or not I've messed with
% redefining element material definitions
%[elem,count]=fscanf(fid,'%i %i %i %i %i %i %i %i %i %i',[10,inf]);
[elem,count]=fscanf(fid,'%i,%i,%i,%i,%i,%i,%i,%i,%i,%i',[10,inf]);
elem=elem';
fclose(fid);

% tell us the size of elem
whos elem

% find which elements contain those nodes and write that to output file
out=fopen('lesion.asc','w');
disp('Opening lesions.asc for writing...');

fprintf(out,'*ELEMENT_SOLID\n');
% go through all of the elements and see if any of the nodes
% for those elements exist in the lesion_nodes matrix
for i=1:size(elem,1),
  % skip the first two columns (elem ID and part ID); just look
  % at nodes associated with each element
  for j=3:10,
    m = find(lesion_nodes==elem(i,j));
      if(m ~= 0)
	fprintf(out,'%i,2,%i,%i,%i,%i,%i,%i,%i,%i \n',elem(i,1),elem(i,3),elem(i,4),elem(i,5),elem(i,6),elem(i,7),elem(i,8),elem(i,9),elem(i,10));
	break;
      elseif(j == 10)
	fprintf(out,'%i,1,%i,%i,%i,%i,%i,%i,%i,%i \n',elem(i,1),elem(i,3),elem(i,4),elem(i,5),elem(i,6),elem(i,7),elem(i,8),elem(i,9),elem(i,10));
      end;
  end;
end;	
		
fprintf(out,'*END\n');
disp('Done writing lesion.asc');
fclose(out);
