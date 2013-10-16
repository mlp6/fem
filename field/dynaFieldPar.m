function [intensity,FIELD_PARAMS] = dynaFieldPar(FIELD_PARAMS, numWorkers)
% allocate number of workers
currentWorkers = matlabpool('size');
isPoolOpen = (currentWorkers > 0);
if (isPoolOpen)
    matlabpool close;
end

maximumNumWorkers = feature('numCores'));

if (nargin == 2)
    if (numWorkers <= maximumNumWorkers)
        matlabpool('open', numWorkers);
    else
        error('Invalid number of workers. Maximum is %i.', maximumNumWorkers)
    end
else
    matlabpool('open', maximumNumWorkers);
end


spmd
    % separate the matrices such that each core gets a roughly equal number
    % of measurement points to perform calculations on.
    % also, distributes matrices based on columns, rather than rows.
    codistPoints = codistributed(FIELD_PARAMS.measurementPoints, codistributor('1d', 1));
    pointsSize = size(FIELD_PARAMS.measurementPoints);
    
    
    FIELD_PARAMS.measurementPoints = getLocalPart(codistPoints);
    [intensityCodist,FIELD_PARAMS]=dynaField(FIELD_PARAMS);
    
    % combine all the separate matrices again.
    intensityDist = codistributed.build(intensityCodist, codistributor1d(2, codistributor1d.unsetPartition, [1 pointsSize(1)]));
end
intensity = gather(intensityDist);
matlabpool close
