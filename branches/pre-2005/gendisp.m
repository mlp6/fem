function []=gen_lat_disp(no_d3plot,axis_flag,res_flag);
% function []=gen_lat_disp(no_d3plot,axis_flag,res_flag);
% create plots of nodal displacements along one of the three
% principal axes in the FEM models
% INPUT:
% 		no_d3plot - number of node*.asc files to process
%		axis_flag - which axis to plot through focus
%				(1-x, 2-y, 3-z)
%		res_flag - 0 -> use node*.asc files
%		           1 -> use zdisp.mat file
% OUTPUT:	disp.mat is saved -> BE SURE TO RENAME IT!!
% mark 04/26/03
[nodes,node_coord]=grab_nodes('/moredata/mlp6/arfi9_elegra/arfi9.dyn',axis_flag);
node_coord=-node_coord;
if(res_flag == 0),
	for i=1:no_d3plot,
		fname=sprintf('node_disp_t%i.asc',i);
		[zdisp_time]=grab_zdisp(fname,nodes);
		zdisp_t(i,:)=zdisp_time;
		disp(i)
	end;
elseif(res_flag == 1),
	load zdisp.mat
	axdisp = zdisp;
	clear zdisp
	disp('loading in displacements from zdisp.mat...')
	for j=1:no_d3plot,
		for i = 1:length(nodes),
			[m,k]=find(nodes(i) == axdisp(:,1,j));
	       		 % get the z-disp for the defined nodes
       			zdisp(i)=axdisp(m,4,j);
		end;
		zdisp_t(j,:) = zdisp;
		disp(j)
	end;
end;
zdisp_t = -zdisp_t * 1e4;
t=1:no_d3plot;
t=t*1e-4;
save disp.mat zdisp_t t node_coord
