function n=plot_mesh(X,Y,Z,C,A);
%
% n=plot_mesh(X,Y,Z,C,A);
%
% X,Y,Z = Grid points
% C     = Color for those points
% A     = [minx maxx miny maxy minz maxz] in nodes
%
% Initial version 4/25/02 Stephen McAleavey
%
minx=A(1);
maxx=A(2);
miny=A(3);
maxy=A(4);
minz=A(5);
maxz=A(6);

h_state=ishold;
surf(squeeze(X(miny:maxy,minx:maxx,minz)),squeeze(Y(miny:maxy,minx:maxx,minz)),squeeze(Z(miny:maxy,minx:maxx,minz)),squeeze(C(miny:maxy,minx:maxx,minz)));
hold on;
surf(squeeze(X(miny:maxy,minx:maxx,maxz)),squeeze(Y(miny:maxy,minx:maxx,maxz)),squeeze(Z(miny:maxy,minx:maxx,maxz)),squeeze(C(miny:maxy,minx:maxx,maxz)));
surf(squeeze(X(miny,minx:maxx,minz:maxz)),squeeze(Y(miny,minx:maxx,minz:maxz)),squeeze(Z(miny,minx:maxx,minz:maxz)),squeeze(C(miny,minx:maxx,minz:maxz)));
surf(squeeze(X(maxy,minx:maxx,minz:maxz)),squeeze(Y(maxy,minx:maxx,minz:maxz)),squeeze(Z(maxy,minx:maxx,minz:maxz)),squeeze(C(maxy,minx:maxx,minz:maxz)));
surf(squeeze(X(miny:maxy,minx,minz:maxz)),squeeze(Y(miny:maxy,minx,minz:maxz)),squeeze(Z(miny:maxy,minx,minz:maxz)),squeeze(C(miny:maxy,minx,minz:maxz)));
surf(squeeze(X(miny:maxy,maxx,minz:maxz)),squeeze(Y(miny:maxy,maxx,minz:maxz)),squeeze(Z(miny:maxy,maxx,minz:maxz)),squeeze(C(miny:maxy,maxx,minz:maxz)));
if (~h_state), hold off, view(30,30); end;

