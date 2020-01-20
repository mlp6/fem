function [] = OptiStruct2DYNA(optiStructIn,DYNAout)

if isempty(strfind(optiStructIn,'.fem'))
    optiStructIn = [optiStructIn '.fem']; 
end

if isempty(strfind(DYNAout,'.k'))
    DYNAout = [DYNAout '.k']; 
end

[optStrNodes,optStrSolid,optStrShell,optStrFlags] = OptiStruct_getElemNodes(optiStructIn);

if ~isempty(optStrFlags)
    disp('OptiStruct completed with errors. Consult OptiStruct_getElemNodes.m')
end

disp('Writing DYNA file.')
fid = fopen(DYNAout,'w');
fprintf(fid,'*KEYWORD\n');
fprintf(fid,'*NODE\n');
fprintf(fid,'%i,%f,%f,%f,0,0\n',optStrNodes');
if ~isempty(optStrShell.tria)
    fprintf(fid,'*ELEMENT_SHELL\n');
    fprintf(fid,'%i,%i,%i,%i,%i,%i,%i,%i,%i,%i\n',[optStrShell.tria optStrShell.tria(:,end) zeros(size(optStrShell.tria,1),4)]');
end
if ~isempty(optStrShell.quad)
    fprintf(fid,'*ELEMENT_SHELL\n');
    fprintf(fid,'%i,%i,%i,%i,%i,%i,%i,%i,%i,%i\n',[optStrShell.quad zeros(size(optStrShell.quad,1),4)]');
end
if ~isempty(optStrSolid.tet)
    fprintf(fid,'*ELEMENT_SOLID\n');
    fprintf(fid,'%i,%i,%i,%i,%i,%i,%i,%i,%i,%i\n',[optStrSolid.tet repmat(optStrSolid.tet(:,end),1,4)]');
end
if ~isempty(optStrSolid.hex)
    fprintf(fid,'*ELEMENT_SOLID\n');
    fprintf(fid,'%i,%i,%i,%i,%i,%i,%i,%i,%i,%i\n',[optStrSolid.hex]');
end
fprintf(fid,'*END');
fclose(fid);
disp('DYNA file written.');