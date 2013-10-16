function [intensity,FIELD_PARAMS] = dynaFieldPar(FIELD_PARAMS)
% open matlabpool
numWorkers = matlabpool('size');
isPoolOpen = (numWorkers > 0);
if(~isPoolOpen)
    matlabpool open;
end

spmd
    % separate the matrices such that each core gets a roughly equal number
    % of measurement points to perform calculations on.
    % also, distributes matrices based on columns, rather than rows.
    codistPoints = codistributed(FIELD_PARAMS.measurementPoints, codistributor('1d', 1));
    pointsSize = size(FIELD_PARAMS.measurementPoints);
    
    % perform calculations on different workers
    switch labindex
        case 1
            FIELD_PARAMS.measurementPoints = getLocalPart(codistPoints);
            [intensityCodist,FIELD_PARAMS]=dynaField(FIELD_PARAMS);
        case 2
            FIELD_PARAMS.measurementPoints = getLocalPart(codistPoints);
            [intensityCodist,FIELD_PARAMS]=dynaField(FIELD_PARAMS);
    end 
    
    % combine all the separate matrices again.
    intensityDist = codistributed.build(intensityCodist, codistributor1d(2, codistributor1d.unsetPartition, [1 pointsSize(1)]));
end
intensity = gather(intensityDist);
matlabpool close
