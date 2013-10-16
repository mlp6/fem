function [intensity,FIELD_PARAMS] = dynaFieldPar(FIELD_PARAMS, numWorkers)
% open matlabpool
currentWorkers = matlabpool('size');
isPoolOpen = (currentWorkers > 0);
if (isPoolOpen)
    matlabpool close;
end

if (nargin == 2)
    if (numWorkers <= feature('numCores'))
        matlabpool('open', numWorkers);
    else
        error('Invalid number of workers. Maximum is %i.', feature('numCores'))
    end
else
    matlabpool('open');
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
