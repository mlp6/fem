% nodeHist.m - post-process node history files from ls-prepost2
% Mark 05/22/07

nodes = load('zdispDataNodes.asc');

for i=1:length(nodes),
    temp = load(sprintf('n%i.asc',nodes(i,1)));
    if(i == 1),
        time = temp(:,1)*1e3; % ms
        lat = nodes(:,2);
    end;
    latLine(i,:) = -1e4*temp(:,2)';
end;

maxDisp = max(max(latLine(:,:)));
minDisp = min(min(latLine(:,:)));
maxlat = max(lat);

figure;
for t=2:length(time),
    plot(lat,latLine(:,t));
    axis([0 maxlat minDisp maxDisp]);
    title(pwd);
    xlabel('Lateral Position (cm)');
    ylabel('z-displacement (\mum)');
    M(t-1) = getframe;
    text(maxlat*0.75,maxDisp*0.75,sprintf('%.1f ms',time(t)));
end;

save zdisp.mat *
