function makePMLhelper(nx,ny,nz,PMLthickness,PID,symmetry,nodein,elemin,elemout)

%PML Helper function for example useage
%
% nx - number of divisions in x dimension
% ny - number of divisions in y dimension
% nz - number of divisions in z dimension
% PMLthickness - thickness of PML layer (between 5-10)
% PID - Part ID to assign to PML
% symmetry - symmetry condition ('q','h',or 'n')
% nodein - input node file name string
% elemin - input elem file name string
% elemout - output elem file name string
%
% Author - Chris Moore 8/27/2014
% Update - CJM - Removed hardcode symmetry
pmlNodeConstraints(nodein,symmetry);
addPML(nx,ny,nz,PMLthickness,PID,symmetry,elemin,elemout)