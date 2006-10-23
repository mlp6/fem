% script to generate file to fix the symmetry plane csnstraints on the 61a
% model (edges do not have BCs)
% mark 09/13/02

fname='sym_bc_arfi7.asc';
[nodes,node_coord]=grab_centerplane('/home/mlp6/arfi/arfi61a.dyn');
fid=fopen(fname,'w');
for i=1:length(nodes)
	if(node_coord(i,3)~=-3.75)
		fprintf(fid,'%d,0,1,0,0,0,1,1 \n',nodes(i));
	end;
	if(node_coord(i,3)==-3.75)
		fprintf(fid,'%d,0,1,0,1,0,1,1 \n',nodes(i));
	end;	
end;	
fclose(fid);
