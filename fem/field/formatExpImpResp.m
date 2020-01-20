function [impulseResponse]=formatExpImpResp(FIELD_PARAMS)
% function [impulseResponse]=formatExpImpResp(FIELD_PARAMS)
%
% Format the raw oscilloscope data to create an impulse response vector that
% can be used by Field II
%
% INPUT:
%   FIELD_PARAMS (struct) - structure of run time parameters
%
% OUTPUT:
%   impulseResponse (float vector) - experimentally-measured impulse response
%   that has been centered and sampled correctly
%
% Mark 06/20/07

SampFreq = FIELD_PARAMS.samplingFrequency;

% read in the raw data from the oscilloscope
if(exist(sprintf('%s.pul',FIELD_PARAMS.Transducer))),
    OscPulse = eval(sprintf('load(''%s.pul'')',FIELD_PARAMS.Transducer));
else,
    error(sprintf('The file %s.pul does not exist in the CWD.',FIELD_PARAMS.Transducer));
end;

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
