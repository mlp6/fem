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
        fid = fopen(sprintf('node_disp_t%i.asc',i),'r');
        tempscan = textscan(fid,'%f32%f32%f32%f32','HeaderLines',4,'CommentStyle','*');
        tempmat = cell2mat(tempscan);
        zdisp(:,:,i) = tempmat;
        clear tempscan tempmat;
end;

% convert to double precision to work w/ downstream functions
zdisp = double(zdisp);

disp('Saving zdisp.mat file')
save zdisp.mat zdisp
