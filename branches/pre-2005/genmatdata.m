function []=genmatdata(imax)
%function []=genmatdata(imax)
% imax - max index of *.asc file to read in
% read in *.asc files from ls-post and save result data to a *.mat file 
% for future matlab processing (trying to save disk space)
% mark 01/31/03

[readnode]=read_dyna_nodes('/home/mlp6/arfi/arfi7.dyn');
nodes=readnode(:,1);
node_coords=readnode(:,2:4);
disp('node and node coordinate matrices created')

for i=1:imax,
	fname=sprintf('node_disp_t%i.asc',i);
	[zdisp]=grab_zdisp(fname,nodes);
	zdispt(i,:)=zdisp;
	disp(i)
end;
zdispt=-zdispt*1e4;
t=1:1:100;
t=t*1e-1;

save zdisp.mat zdispt t node_coords nodes
disp('zdisp.mat file created')
