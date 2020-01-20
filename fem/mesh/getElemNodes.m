function [nodes,elem_solid,elem_shell,elem_beam] = getElemNodes(kFile)

% note that this is left general (outputs all columns) for robustness:
% DYNA includes zeros in extra columns, remove these as needed (e.g. you
% only need columns 1-4 for nodes, but 5 and 6 are left included. More
% important for elements where columns vary by element type. Based on
% python script from MPalmeri.


if isempty(strfind(kFile,'.k'))
    kFile = [kFile '.k']; 
end
      
nodes = [];
elem_solid = [];
elem_shell = [];
elem_beam = [];


%extract elements and nodes
fid = fopen(kFile,'r');
inEl_slid = false;
inEl_shel = false;
inEl_beam = false;
inN = false;
while ~feof(fid)
    t = fgetl(fid);
    if (t(1) == '*' && (inN || inEl_slid || inEl_shel || inEl_beam))
        if inEl_slid
            inEl_slid = false;
        end
        if inEl_shel
            inEl_shel = false;
        end
        if inEl_beam
            inEl_beam = false;
        end        
        if inN
            inN = false;
        end
    end
    if strfind(t,'*ELEMENT_SOLID')
        inEl_slid = true;
        t = fgetl(fid);
    end
    if strfind(t,'*ELEMENT_SHELL')
        inEl_shel = true;
        t = fgetl(fid);
    end
    if strfind(t,'*ELEMENT_BEAM')
        inEl_beam = true;
        t = fgetl(fid);
    end
    if strfind(t,'*NODE')
        inN = true;
        t = fgetl(fid);
    end
    if inEl_slid || inEl_shel || inEl_beam || inN
        if t(1) ~= '$'
            if inEl_slid
                t = str2num(t); %#ok<ST2NM>
                elem_solid(end+1,:) = t; %#ok<AGROW>
            end
            if inEl_shel
                t = str2num(t); %#ok<ST2NM>
                elem_shell(end+1,:) = t; %#ok<AGROW>
            end
            if inEl_beam
                t = str2num(t); %#ok<ST2NM>
                elem_beam(end+1,:) = t; %#ok<AGROW>
            end
            if inN
                t = str2num(t); %#ok<ST2NM>
                nodes(end+1,:) = t; %#ok<AGROW>
            end
        end
    end     
end
fclose(fid);
end