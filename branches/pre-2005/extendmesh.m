% SCRIPT DESCRIPTION AND MODIFICATION HISTORY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% modified this code to extend the arfi8 mesh axially
% mark 03/25/03
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% this is a script to extend the mesh laterally to help prevent the 
% high-attenuation models from have reflected shear waves from
% distorting the results
%
% note - hm was having problems growing this mesh (i.e. adding new
% elements laterally), so i am working around this by changing the lateral
% coordinates of the pre-existing nodes, which helps to preserve some
% of the other scripts that are hard-coded
%
% mark 11/24/02

endofline=sprintf('\n');
fid=fopen('/moredata/mlp6/arfi8_elegra/nodes.asc','r');
s=fscanf(fid,'%s',1);
while (~strcmp(s,'*NODE')),
        s=fscanf(fid,'%s',1);
        end;
c=fscanf(fid,'%c',1);
while(c~=endofline);
        c=fscanf(fid,'%c',1);
        end;
disp('reading in center axis node data...')
[nodedata,count]=fscanf(fid,'%i %f %f %f',[4,inf]);
nodedata=nodedata';
fclose(fid);

% print out new node listing with stretched lateral dimension
fid = fopen('newnodelist.asc','w');
for i=1:length(nodedata),
	if(nodedata(i,4) < -2.49)
		fprintf(fid,'%i,%f,%f,%f\n',nodedata(i,1),nodedata(i,2),...
			nodedata(i,3),nodedata(i,4)-0.15);
	elseif(nodedata(i,4) < -2.45 & nodedata(i,4) > -2.48)
		fprintf(fid,'%i,%f,%f,%f\n',nodedata(i,1),nodedata(i,2),...
			nodedata(i,3),nodedata(i,4)-0.07);
	elseif(nodedata(i,4) < -2.41 & nodedata(i,4) > -2.44)
                fprintf(fid,'%i,%f,%f,%f\n',nodedata(i,1),nodedata(i,2),...
                        nodedata(i,3),nodedata(i,4)-0.02);
	else
		fprintf(fid,'%i,%f,%f,%f\n',nodedata(i,1),nodedata(i,2),...
			nodedata(i,3),nodedata(i,4));
	end;
end;
fclose(fid)
