function []=createvms(NoFiles)
% function []=createvms(NoFiles);
% INPUT:  NoFiles - number of t*.asc files to convert
% OUTPUT: vms.mat is written to CWD
% Mark 06/25/08

disp('Reading in ASCII data files');
for i=1:NoFiles,
	disp(sprintf('Working on file %i of %i',i,NoFiles));
        fid = fopen(sprintf('node_vms_t%i.asc',i),'r');
        tempscan = textscan(fid,'%f32%f32','HeaderLines',5,'CommentStyle','*');
        tempmat = cell2mat(tempscan);
        vms(:,:,i) = tempmat;
        clear tempscan tempmat;
end;

% convert to double precision to work w/ downstream functions
vms = double(vms);

disp('Saving vms.mat file')
save vms.mat vms
