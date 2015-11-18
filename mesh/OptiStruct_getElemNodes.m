function [nodes,elem_solid,elem_shell,errorFlags] = OptiStruct_getElemNodes(optStr_File)
%%
%v1 - 20150604 
%pull elements and nodes from optistruct files. currently does not support
%beam elements.

errorFlags = [];
% 1 - unmatched triangle elements
% 2 - unmatched     quad elements
% 3 - unmatched      tet elements
% 4 - unmatched      hex elements

if isempty(strfind(optStr_File,'.fem'))
    optStr_File = [optStr_File '.fem']; 
end      
nodes = [];
elemPartList = [];
elem_solid.tet = [];
elem_solid.hex = [];
elem_shell.quad = [];
elem_shell.tria = [];
% elem_beam = [];

%extract elements and nodes
fid = fopen(optStr_File,'r');

%set up section flags
inEl_slid = false;
inEl_shel = false;
% inEl_beam = false;
inN = false;
inPartList = false;

%%
%loop through the file
disp('Reading OptiStruct file.');
while ~feof(fid)
    t = fgetl(fid);
    %make sure the line isn't empty
    while isempty(t) && ~feof(fid)
        t = fgetl(fid);
    end
    
    %% 
    % If we reach a comment line, get out of the current section. Exception
    % for part numbering, which is in comments for optistruct files:
    
    if (t(1) == '$' && (inN || inEl_slid || inEl_shel || inPartList))
        
        %exit the solid section
        if inEl_slid
            inEl_slid = false;
        end
        
        %exit the shell section
        if inEl_shel
            inEl_shel = false;
        end
        
%         if inEl_beam
%             inEl_beam = false;
%         end 
        
        %exit the node section
        if inN
            inN = false;
        end
        
        %exit the part list section
        if inPartList && all(isstrprop(t(2:end),'wspace')) %line has values
            inPartList = false;
            %reorganize rangeList for parsing
            rangeList = rangeList(2:end,:)';
            rangeList = rangeList(:);
            rangeListEmpty = cellfun(@isempty,rangeList);
            rangeList = rangeList(~rangeListEmpty);
            clear rangeListEmpty
            
            %loop through rangeList, assigning ID intervals
            counter = 1;
            while counter <= length(rangeList)
                if ~isempty(str2double(rangeList(counter))) %is a number
                    if counter == length(rangeList) || isempty(strfind(rangeList{counter + 1},'THRU'))
                        elemPartList(end+1,:) = [currPart str2double(rangeList(counter)) str2double(rangeList(counter))];
                        counter = counter + 1;
                    else
                        elemPartList(end+1,:) = [currPart str2double(rangeList(counter)) str2double(rangeList(counter+2))];
                        counter = counter + 3;
                    end 
                end
            end
            
            %cleanup
            clear currPart rangeList counter
        end
    end
    
    %% 
    % determine if we found a section of interest:
    
    %section is a part numbering section
    if ~isempty(strfind(t,'HMMOVE'))
        inPartList = true;
        currPart = str2double(t(9:end));
        rangeList{1,9} = [];
        t = fgetl(fid);
    end
    %section is solid elements
    if ~isempty(strfind(t,'CHEXA')) || ~isempty(strfind(t,'TETRA'))
        inEl_slid = true;
    end
    %section is shell elements
    if ~isempty(strfind(t,'CQUAD4')) || ~isempty(strfind(t,'CTRIA3'))
        inEl_shel = true;
    end
    
%     if strfind(t,'*ELEMENT_BEAM')
%         inEl_beam = true;
%         t = fgetl(fid);
%     end

    %section is nodes
    if ~isempty(strfind(t,'GRID'))
        inN = true;
    end
    
    %%
    %if we're in a section of interest, add to output lists:
    if inEl_slid || inEl_shel || inN || inPartList
        if t(1) ~= '$'  %not in a comment section
            
            %add to solids
            if inEl_slid
                if strfind(t,'CHEXA') %current line is a hex line
                    elID = str2double(t(9:16));
                    n1 = str2double(t(25:32));
                    n2 = str2double(t(33:40));
                    n3 = str2double(t(41:48));
                    n4 = str2double(t(49:56));
                    n5 = str2double(t(57:64));
                    n6 = str2double(t(65:72));
                    t = fgetl(fid);
                    n7 = str2double(t(9:16));
                    n8 = str2double(t(17:24));
                    elem_solid.hex(end+1,:) = [elID 0 n1 n2 n3 n4 n5 n6 n7 n8];
                    clear nID n1 n2 n3 n4 n5 n6 n7 n8
                else %current line is a tet line
                    elID = str2double(t(9:16));
                    n1 = str2double(t(25:32));
                    n2 = str2double(t(33:40));
                    n3 = str2double(t(41:48));
                    n4 = str2double(t(49:56));
                    elem_solid.tet(end+1,:) = [elID 0 n1 n2 n3 n4];
                    clear nID n1 n2 n3 n4
                end
            end
            
            %add to shells
            if inEl_shel
                if strfind(t,'CQUAD4') %current line is a quad line
                    elID = str2double(t(9:16));
                    n1 = str2double(t(25:32));
                    n2 = str2double(t(33:40));
                    n3 = str2double(t(41:48));
                    n4 = str2double(t(49:56));
                    elem_shell.quad(end+1,:) = [elID 0 n1 n2 n3 n4];
                    clear nID n1 n2 n3 n4
                else %current line is a tria line
                    elID = str2double(t(9:16));
                    n1 = str2double(t(25:32));
                    n2 = str2double(t(33:40));
                    n3 = str2double(t(41:48));
                    elem_shell.tria(end+1,:) = [elID 0 n1 n2 n3];
                    clear nID n1 n2 n3
                end
            end
            
%             if inEl_beam
%                 t = str2num(t); %#ok<ST2NM>
%                 elem_beam(end+1,:) = t; %#ok<AGROW>
%             end
            
            %add to nodes
            if inN
                t1 = str2double(t(9:16));
                
                %check for scientific notation in node XYZ coordinates
                t2 = t(25:32);
                if strfind(t2,'-')
                    minusIND = find(t2 == '-',1,'last');
                    if minusIND ~= 1 && ~isstrprop(t2(minusIND-1),'wspace')
                        t2 = [t2(1:minusIND-1) 'E' t2(minusIND:end)];
                    end
                elseif strfind(t2,'+')
                    plusIND = find(t2 == '+',1,'last');
                    t2 = [t2(1:plusIND-1) 'E' t2(plusIND:end)];
                end
                t3 = t(33:40);
                if strfind(t3,'-')
                    minusIND = find(t3 == '-',1,'last');
                    if minusIND ~= 1 && ~isstrprop(t3(minusIND-1),'wspace')
                        t3 = [t3(1:minusIND-1) 'E' t3(minusIND:end)];
                    end
                elseif strfind(t3,'+')
                    plusIND = find(t3 == '+',1,'last');
                    t3 = [t3(1:plusIND-1) 'E' t3(plusIND:end)];
                end
                t4 = t(41:48);
                if strfind(t4,'-')
                    minusIND = find(t4 == '-',1,'last');
                    if minusIND ~= 1 && ~isstrprop(t4(minusIND-1),'wspace')
                        t4 = [t4(1:minusIND-1) 'E' t4(minusIND:end)];
                    end
                elseif strfind(t4,'+')
                    plusIND = find(t4 == '+',1,'last');
                    t4 = [t4(1:plusIND-1) 'E' t4(plusIND:end)];
                end
                %convert to double
                t2 = str2double(t2);
                t3 = str2double(t3);
                t4 = str2double(t4);
                %add to node list
                nodes(end+1,:) = [t1 t2 t3 t4]; %#ok<AGROW>
                clear t1 t2 t3 t4
            end
        else %this is a comments section
            
            %section is a part ID section
            if inPartList
                numEntries = floor(length(t)/8)-1; %first field is $
                entry{1,9} = [];
                for i = 1:numEntries
                    entry{i} = t((i*8)+1:(i+1)*8);
                end
                    rangeList = [rangeList;entry];
                    clear entry i
            end
        end
    end     
end

%finished with the input file
fclose(fid);
disp('Finished reading OptiStruct file. Assigning part IDs...');

%%
%sort the partID section for faster sorting
elemPartList = sortrows(elemPartList,2);

%add part numbers to triangle elements
if ~isempty(elem_shell.tria)
    for i = 1:size(elem_shell.tria,1)
        elemIND = find([(elem_shell.tria(i,1) >= elemPartList(:,2)) + (elem_shell.tria(i,1) <= elemPartList(:,3))] == 2,1,'first');
        elem_shell.tria(i,2) = elemPartList(elemIND,1);
    end
    if any(elem_shell.tria(:,2) == 0)
        elem_shell.tria(elem_shell.tria(:,2) == 0,2) = 99999991;
        errorFlags = [errorFlags, 1];
    end
end
%add part numbers to quad elements
if ~isempty(elem_shell.quad)
    for i = 1:size(elem_shell.quad,1)
        elemIND = find([(elem_shell.quad(i,1) >= elemPartList(:,2)) + (elem_shell.quad(i,1) <= elemPartList(:,3))] == 2,1,'first');
        elem_shell.quad(i,2) = elemPartList(elemIND,1);
    end
    if any(elem_shell.quad(:,2) == 0)
        elem_shell.quad(elem_shell.quad(:,2) == 0,2) = 99999992;
        errorFlags = [errorFlags, 2];
    end
end
%add part numbers to tet elements
if ~isempty(elem_solid.tet)
    for i = 1:size(elem_solid.tet,1)
        elemIND = find([(elem_solid.tet(i,1) >= elemPartList(:,2)) + (elem_solid.tet(i,1) <= elemPartList(:,3))] == 2,1,'first');
        elem_solid.tet(i,2) = elemPartList(elemIND,1);
    end
    if any(elem_solid.tet(:,2) == 0)
        elem_solid.tet(elem_solid.tet(:,2) == 0,2) = 99999993;
        errorFlags = [errorFlags, 3];
    end
end
%add part numbers to hex elements
if ~isempty(elem_solid.hex)
    for i = 1:size(elem_solid.hex,1)
        elemIND = find([(elem_solid.hex(i,1) >= elemPartList(:,2)) + (elem_solid.hex(i,1) <= elemPartList(:,3))] == 2,1,'first');
        elem_solid.hex(i,2) = elemPartList(elemIND,1);
    end
    if any(elem_solid.hex(:,2) == 0)
        elem_solid.hex(elem_solid.hex(:,2) == 0,2) = 99999994;
        errorFlags = [errorFlags, 4];
    end
end

%flag any elements that didn't get a part number assigned.
if ~isempty(errorFlags)
    for i = 1:length(errorFlags)
        switch errorFlags(i)
            case 1
                disp('Warning: Triangles in OptiStruct file without partIDs. Assigned to 99999991.');
            case 2
                disp('Warning: Quads in OptiStruct file without partIDs. Assigned to 99999992.');
            case 3
                disp('Warning: Tets in OptiStruct file without partIDs. Assigned to 99999993.');
            case 4
                disp('Warning: Hexes in OptiStruct file without partIDs. Assigned to 99999994.');
        end
    end
end
disp('Finished assigning Part IDs. OptiStruct input complete.');

%end OptiStruct_getElemNodes.m
end