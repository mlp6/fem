load /emfd/mlp6/CIRS_FEM/kathy_focal_hawaii/centerplane.mat
load zdisp.mat
%index = zeros(max(zdisp(:,1,1)),1);
data(zdisp(:,1,1)) = zdisp(:,4,3);

disp = -data(nodefind)*1e4;

ax = (1:size(nodefind,1))*0.2;
lat = (1:size(nodefind,2))*0.2;

imagesc(lat,ax,disp,[0 20])
xlabel('Lateral Position (mm)')
ylabel('Axial Position (mm)')
