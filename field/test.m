function [intensity,FIELD_PARAMS] = test(FIELD_PARAMS)
% tic;
numWorkers = matlabpool('size');
isPoolOpen = (numWorkers > 0);
if(~isPoolOpen)
    matlabpool open;
end

spmd
    codistPoints = codistributed(FIELD_PARAMS.measurementPoints, codistributor('1d', 1));
    a = size(FIELD_PARAMS.measurementPoints);
    switch labindex
        case 1
            FIELD_PARAMS.measurementPoints = getLocalPart(codistPoints);
            [intensityCodist,FIELD_PARAMS]=dynaField(FIELD_PARAMS);
        case 2
            FIELD_PARAMS.measurementPoints = getLocalPart(codistPoints);
            [intensityCodist,FIELD_PARAMS]=dynaField(FIELD_PARAMS);
    end 
    intensityDist = codistributed.build(intensityCodist, codistributor1d(2, codistributor1d.unsetPartition, [1 a(1)]));
end
intensity = gather(intensityDist);
matlabpool close

% CalcTime = toc; % s
% ActualRunTime = CalcTime/60; % min
% disp(sprintf('Parallel Actual Run Time = %.3f m\n',ActualRunTime));