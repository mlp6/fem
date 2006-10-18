function []=createzdisp(NoFiles)
% function []=createzdisp(NoFiles);
% INPUT:  NoFiles - number of t*.asc files to convert
% OUTPUT: zdisp.mat is written to CWD
% Mark 05/17/04
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Modified to convert zdisp to single precision to save
% disk space when saved.
% Mark 04/14/05
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

disp('Reading in ASCII data files');
for i=1:NoFiles,
	disp(sprintf('Working on file %i of %i',i,NoFiles));
	cmd = sprintf('[zdisp(:,:,%i)]=load(''t%i.asc'');',i,i);
	eval(cmd);
end;

% convert the single-precision data
disp('Converting to single precision data (and back)');
zdisp = single(zdisp);
zdisp = double(zdisp);

disp('Saving zdisp.mat file')
save zdisp.mat zdisp
