% script to generate spatial derivative plots from the FEM data sets
% this is all hard-coded!!
% mark 11/14/03

disp('reading in node locations...')
[node_loc]=read_dyna_nodes('cirs.dyn');

disp('loading in displacement data...')
load zdisp.mat;

% first do this for the axial displacements
disp('sorting axial displacements...')
value = zdisp(:,4,3);
[A,axdisp,lat,ax]=sortdata(node_loc,value,1);
axdisp = -axdisp*1e4;

% next for the lateral displacements
disp('sorting lateral displacements...')
value = zdisp(:,3,3);
[A,latdisp,lat,ax]=sortdata(node_loc,value,1);
latdisp = -latdisp*1e4;

% next for the elevation displacements
disp('sorting elevation displacements...')
value = zdisp(:,2,3);
[A,eledisp,lat,ax]=sortdata(node_loc,value,1);
eledisp = -eledisp*1e4;

clear value
whos

save waves.mat A axdisp latdisp eledisp ax lat
