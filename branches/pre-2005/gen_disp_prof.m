function []=gen_plot(no_d3plot);
% function []=gen_plot(no_d3plot);
[nodes,node_coord]=grab_nodes('/moredata/mlp6/arfi8_elegra/nodes.asc');
node_coord=-node_coord;
for i=1:no_d3plot,
	fname=sprintf('node_disp_t%i.asc',i);
	[zdisp_time]=grab_zdisp(fname,nodes);
	zdisp_t(i,:)=zdisp_time;
	disp(i)
end;
zdisp_t = -zdisp_t * 1e4;
t=1:no_d3plot;
t=t*1e-4;
save disp_prof.mat zdisp_t t node_coord
