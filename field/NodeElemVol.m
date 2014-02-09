function NodeElemVol(nodeName, elemName, NodeVolName)
%   NodeElemVol - Uses input arguments containing the coordinates of nodes at
%   each mesh and a list of elements and their corresponding 8 nodes, and
%   computes the volume of each element and the average volume of the 8
%   elements surronuding each node. Element volumes are computed by dividing
%   each element into three unique hyper-pyramids as shown here: 
%   http://www.physicsinsights.org/pyramids-1.html
%
%   nodeElem - name of nodes file
%   elemName - name of elements file
%   NodeVolName - name of output node volume file
    
    % read in the nodes
    fid = fopen(nodeName,'r');
    nodes=textscan(fid,'%f%f%f%f','CommentStyle','*','Delimiter',',');
    fclose(fid);
    nodes = cell2mat(nodes);
    
    % read in elems
    fid = fopen(elemName,'r');
    elems=textscan(fid,'%f%f%f%f%f%f%f%f%f%f','CommentStyle','*','Delimiter',',');
    fclose(fid);
    elems = cell2mat(elems);
    
    % construct map of node IDs to x, y, z coordinates from nodes.dyn
    fprintf('Mapping node IDs to their coordinates...\n')
    nodeMap = containers.Map('KeyType', 'int32', 'ValueType', 'any');
    for i = 1:length(nodes)
        nodeMap(nodes(i, 1)) = nodes(i, 2:4);
    end
    
    % construct map of elem IDs to node IDs from elems.dyn
    fprintf('Mapping element IDs to their node IDs...\n')
    elemMap = containers.Map('KeyType', 'int32', 'ValueType', 'any');
    for i = 1:length(elems)
        elemMap(elems(i, 1)) = elems(i, 3:10);
    end

    
    % create map of elem IDs to their volumes
    elemVolMap = containers.Map('KeyType', 'int32', 'ValueType', 'any');
    
    % begin calculation of element volumes
    fprintf('Calculating element volumes...\n')
    for i = 1:length(elems)
        % get coordinates of each of the eight nodes comprising the i-th
        % element
        node1Coord = nodeMap(elems(i, 3));
        x1 = node1Coord(1);
        y1 = node1Coord(2);
        z1 = node1Coord(3);
        
        node2Coord = nodeMap(elems(i, 4));
        x2 = node2Coord(1);
        y2 = node2Coord(2);
        z2 = node2Coord(3);
        
        node3Coord = nodeMap(elems(i, 5));
        x3 = node3Coord(1);
        y3 = node3Coord(2);
        z3 = node3Coord(3);
        
        node4Coord = nodeMap(elems(i, 6));
        x4 = node4Coord(1);
        y4 = node4Coord(2);
        z4 = node4Coord(3);
        
        node5Coord = nodeMap(elems(i, 7));
        x5 = node5Coord(1);
        y5 = node5Coord(2);
        z5 = node5Coord(3);
        
        node6Coord = nodeMap(elems(i, 8));
        x6 = node6Coord(1);
        y6 = node6Coord(2);
        z6 = node6Coord(3);
        
        node7Coord = nodeMap(elems(i, 9));
        x7 = node7Coord(1);
        y7 = node7Coord(2);
        z7 = node7Coord(3);
        
        node8Coord = nodeMap(elems(i, 10));
        x8 = node8Coord(1);
        y8 = node8Coord(2);
        z8 = node8Coord(3);
        
%         [x1, x2, x3, x4, x5, x6, x7, x8] = deal(nodeMap(elems(i, 3)(1), ...
%             nodeMap(elems(i, 4))(1), nodeMap(elems(i, 5), 1), nodeMap(elems(i, 6), 1), ...
%             nodeMap(elems(i, 7), 1), nodeMap(elems(i, 8), 1), nodeMap(elems(i, 9), 1), ...
%             nodeMap(elems(i, 10), 1));
%         [y1, y2, y3, y4, y5, y6, y7, y8] = deal(nodeMap(elems(i, 3), 2), ...
%             nodeMap(elems(i, 4), 2), nodeMap(elems(i, 5), 2), nodeMap(elems(i, 6), 2), ...
%             nodeMap(elems(i, 7), 2), nodeMap(elems(i, 8), 2), nodeMap(elems(i, 9), 2), ...
%             nodeMap(elems(i, 10), 2));
%         [z1, z2, z3, z4, z5, z6, z7, z8] = deal(nodeMap(elems(i, 3), 3), ...
%             nodeMap(elems(i, 4), 3), nodeMap(elems(i, 5), 3), nodeMap(elems(i, 6), 3), ...
%             nodeMap(elems(i, 7), 3), nodeMap(elems(i, 8), 3), nodeMap(elems(i, 9), 3), ...
%             nodeMap(elems(i, 10), 3));
        
        % calculate the area of the three bases
        
        % base 1
        a = sqrt((x1-x2)^2+(y1-y2)^2+(z1-z2)^2); %a, b, c, d are lengths of 4 sides
        b = sqrt((x2-x3)^2+(y2-y3)^2+(z2-z3)^2);
        c = sqrt((x3-x4)^2+(y3-y4)^2+(z3-z4)^2);
        d = sqrt((x4-x1)^2+(y4-y1)^2+(z4-z1)^2);
        p = sqrt((x1-x3)^2+(y1-y3)^2+(z1-z3)^2); %p, q are lengths of diagonals
        q = sqrt((x2-x4)^2+(y2-y4)^2+(z2-z4)^2);
        
        s = (a+b+c+d) / 2; %s is the semiperimeter of the base
        
        area1 = sqrt((s-a)*(s-b)*(s-c)*(s-d)-0.25*(a*c+b*d+p*q)*(a*c+b*d-p*q));
        
        % base 2
        a = sqrt((x1-x5)^2+(y1-y5)^2+(z1-z5)^2); %a, b, c, d are lengths of 4 sides
        b = sqrt((x5-x6)^2+(y5-y6)^2+(z5-z6)^2);
        c = sqrt((x6-x2)^2+(y6-y2)^2+(z6-z2)^2);
        d = sqrt((x2-x1)^2+(y2-y1)^2+(z2-z1)^2);
        p = sqrt((x1-x6)^2+(y1-y6)^2+(z1-z6)^2); %p, q are lengths of diagonals
        q = sqrt((x2-x5)^2+(y2-y5)^2+(z2-z5)^2);
        
        s = (a+b+c+d) / 2; %s is the semiperimeter of the base
        
        area2 = sqrt((s-a)*(s-b)*(s-c)*(s-d)-0.25*(a*c+b*d+p*q)*(a*c+b*d-p*q));
        
        % base 3
        a = sqrt((x2-x6)^2+(y2-y6)^2+(z2-z6)^2); %a, b, c, d are lengths of 4 sides
        b = sqrt((x6-x7)^2+(y6-y7)^2+(z6-z7)^2);
        c = sqrt((x7-x3)^2+(y7-y3)^2+(z7-z3)^2);
        d = sqrt((x3-x2)^2+(y3-y2)^2+(z3-z2)^2);
        p = sqrt((x2-x7)^2+(y2-y7)^2+(z2-z7)^2); %p, q are lengths of diagonals
        q = sqrt((x3-x6)^2+(y3-y6)^2+(z3-z6)^2);
        
        s = (a+b+c+d) / 2; %s is the semiperimeter of the base
        
        area3 = sqrt((s-a)*(s-b)*(s-c)*(s-d)-0.25*(a*c+b*d+p*q)*(a*c+b*d-p*q));
        
        % Calculate the distance from the apex (node 8) to each of the
        % three planes defined by nodes 1,4,3,2; 1,5,6,2; 2,3,6,7;
        
        % volume 1
        AB = [x4-x1, y4-y1, z4-z1];
        AC = [x2-x1, y2-y1, z2-z1];
        normal = cross(AB, AC);
        [Q, R, S] = deal(normal(1), normal(2), normal(3));
        % normal gives coefficients of plane equation Qx+Ry+Sz+D=0
        D = -Q*x1-R*y1-S*z1; %constant term of plane equation
        
        h1 = abs((Q*x8+R*y8+S*z8+D)/(sqrt(Q^2+R^2+S^2))); %distance from plane to apex
        
        vol1 = area1*h1/3;
        
        % volume 2
        AB = [x2-x1, y2-y1, z2-z1];
        AC = [x5-x1, y5-y1, z5-z1];
        normal = cross(AB, AC);
        [Q, R, S] = deal(normal(1), normal(2), normal(3));
        % normal gives coefficients of plane equation Qx+Ry+Sz+D=0
        D = -Q*x1-R*y1-S*z1; %constant term of plane equation
        
        h2 = abs((Q*x8+R*y8+S*z8+D)/(sqrt(Q^2+R^2+S^2))); %distance from plane to apex
        
        vol2 = area2*h2/3;
        
        % volume 3
        AB = [x3-x2, y3-y2, z3-z2];
        AC = [x6-x2, y6-y2, z6-z2];
        normal = cross(AB, AC);
        [Q, R, S] = deal(normal(1), normal(2), normal(3));
        % normal gives coefficients of plane equation Qx+Ry+Sz+D=0
        D = -Q*x2-R*y2-S*z2; %constant term of plane equation
        
        h3 = abs((Q*x8+R*y8+S*z8+D)/(sqrt(Q^2+R^2+S^2))); %distance from plane to apex
        
        vol3 = area3*h3/3;
        
        % finally, sum the pyramids to get the volume of the element
        % and place it into the map
        elemVolMap(elems(i, 1)) = vol1 + vol2 + vol3;
    end
    
    % map each nodeID to surrounding elemIDs using elems.dyn
    fprintf('Mapping node IDs to surrounding element IDs...\n')
    nodeElemMap = containers.Map('KeyType', 'int32', 'ValueType', 'any');
    for i = 1:length(elems)
        for j = 3:10
            % if node ID already present in the map, get the matrix of
            % element IDs it maps to, then add the current element ID to
            % that matrix
            if (isKey(nodeElemMap, elems(i, j)))
                tempNodeArray = nodeElemMap(elems(i, j));
                tempNodeArray(length(tempNodeArray)+1) = elems(i, 1);
                nodeElemMap(elems(i, j)) = tempNodeArray;
            % if node ID not already present in the map, put a new
            % key-value pair in the map
            else
                nodeElemMap(elems(i, j)) = elems(i, 1);
            end
        end
    end
    
    % now iterate through all the nodes, get the surrounding element IDs
    % using previously created nodeElemMap, and calculate the average of
    % the volumes of those elements, and write them to the NodeVolume file.
    
    fprintf('Generating %s file with %d node volumes\n', NodeVolName, length(nodes))
    fid = fopen(NodeVolName, 'w');
    tstart = tic;
    for i = 1:length(nodes)
        % calculating average volume of surrounding elements
        if (isKey(nodeElemMap, nodes(i, 1)))
            localElems = nodeElemMap(nodes(i, 1));
            sum = 0;
            for j = 1:length(localElems)
                sum = sum + elemVolMap(localElems(j));
            end
            avgVol = sum / length(localElems);
            fprintf(fid, '%d %.11e\n', nodes(i, 1), avgVol);
        end
    end
    fclose(fid);
    fprintf('Finished making %s file in %.2f s\n', NodeVolName, toc(tstart))
end

