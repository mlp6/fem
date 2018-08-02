fid=fopen("myNodes.dyn",'r')
endofline = sprintf('\n');
s = fscanf(fid, '%s', 1);
while (~strcmp(s, '*NODE')),
s = fscanf(fid, '%s', 1);
end
c = fscanf(fid, '%c', 1);
while(c ~= endofline);
c = fscanf(fid, '%c', 1);
end
[mpn] = fscanf(fid, '%d,%f,%f,%f', [4, inf])
mpn = mpn'
mpn(:,4)=-mpn(:,4);
mpn(:,2:3)=[mpn(:,3) mpn(:,2)];
mpn(:,2:4)=mpn(:,2:4)/100;
FIELD_PARAMS.soundSpeed=1540;
FIELD_PARAMS.samplingFrequency = 100e6;
FIELD_PARAMS.measurementPointsandNodes = mpn;
FIELD_PARAMS.alpha = 0.5;
FIELD_PARAMS.alpha = 0.1;
FIELD_PARAMS.Fnum = .1;
focus.x = 2;
focus.y = 1;
focus.z = 1;
FIELD_PARAMS.focus = focus;
FIELD_PARAMS.Frequency = 100.1;
field_init(0)
set_field('c', FIELD_PARAMS.soundSpeed);
set_field('fs', FIELD_PARAMS.samplingFrequency);
set_field('threads', 1);
Th=xdc_convex_focused_array(192,.0002925,.0112,3.25e-05,.0394,.0725,1,7,[0 0 0.02])
tc=gauspuls('cutoff',3e6,.7,-6,-40)
t=-tc:1/100e6:tc;
impulseResponse= gauspuls(t,3e6,.7);
xdc_impulse(Th, impulseResponse)
ThData=xdc_get(Th, 'rect');
FIELD_PARAMS.Th_data = ThData;
exciteFreq=FIELD_PARAMS.Frequency*1e6;
ncyc=50;
texcite=0:1/FIELD_PARAMS.samplingFrequency:ncyc/exciteFreq;
excitationPulse=sin(2*pi*exciteFreq*texcite);
Freq_att=FIELD_PARAMS.alpha*100/1e6;
att_f0=exciteFreq;
att=Freq_att*att_f0;
set_field('att', att);
set_field('Freq_att', Freq_att);
set_field('att_f0', att_f0);
set_field('use_att', 1);
numNodes = size(FIELD_PARAMS.measurementPointsandNodes, 1);
for i = 1:numNodes,
[pressure, startTime] = calc_hp(Th,mpn(i,2:4))
intensity(i)=sum(pressure.*pressure);
end
