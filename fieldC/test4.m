% define the excitation pulse
FIELD_PARAMS.Frequency = 7.2;
FIELD_PARAMS.samplingFrequency = 100e6;

exciteFreq=FIELD_PARAMS.Frequency*1e6;

ncyc=50;

texcite=0:1/FIELD_PARAMS.samplingFrequency:ncyc/exciteFreq;

excitationPulse=sin(2*pi*exciteFreq*texcite);
