% VF105ImpulseResponse
% generate an impulse response vector for the VF10-5 for field simulation 
% re-sampled to a sampling rate of 100 MHz (hard-coded below)
% Mark 01/31/05

% define the sampling frequency
SampFreq = 200e6;

% read in the raw data from the oscilloscope
OscPulse = load('vf105.pul');

TimePulse = OscPulse(:,1);
% normalize the pulse data
Pulse = OscPulse(:,2)./max(OscPulse(:,2));
% center the time axis around the max intensity
[MaxPulse,MaxPulseIndex]=max(Pulse);
TimePulse = TimePulse - OscPulse(MaxPulseIndex,1);

% re-sample the data to match the Field II sampling frequency
NewTime = min(TimePulse):1/SampFreq:max(TimePulse);
NewPulse = interp1(TimePulse,Pulse,NewTime);

% find the indices of NewTime to use for the Field II impulse response
StartIndex = min(find(NewTime > -4e-7));
StopIndex = min(find(NewTime > 4e-7));

impulseResponse = NewPulse(StartIndex:StopIndex);

plot(NewTime(StartIndex:StopIndex),impulseResponse);

save FieldImpulseResponseVF105_200e6.mat impulseResponse SampFreq
