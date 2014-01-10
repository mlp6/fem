function [x, y, z] = GenMeshMatlab(x1, y1, z1, x2, y2, z2, xEle, yEle, zEle)
%GENMESHMATLAB 
%   Using (x1, y1, z1) and (x2, y2, z2) as opposite corners of a meshgrid,
%   creates nodes.dyn and elems.dyn using xEle, yEle, and zEle as the
%   number of x, y, and z elements respectively.
%   Currently assuming that x1 > x2, y1 > y2, z1 > z2.
    

    % based on the node ID of the first corner, nid1, the other node ids
    % can be given by:
    % nid1
    % nid1 + 1 (going down)
    % nid1 + 1 + (xEle + 1) (going down then right)
    % nid1 + (xEle + 1) (going right)
    % This must be done from 1 to 103 (which is zEle + 1)
    % above gives vertices defining an element face in the order given by
    % the right hand rule (outward normal).
    % opposite face:
    % (xEle + 1)(yEle + 1) + nid1 
    % (xEle + 1)(yEle + 1) + nid1 + 1 (going down)
    % (xEle + 1)(yEle + 1) + nid1 + 1 + (xEle + 1) (going down then right)
    % (xEle + 1)(yEle + 1) + nid1 + (xEle + 1) (going right)

    
%     [x, y, z] = meshgrid(linspace(x1, x2, xEle + 1), ...
%                          linspace(y1, y2, yEle + 1), ...
%                          linspace(z1, z2, zEle + 1));
    x = linspace(x2, x1, xEle + 1)
    y = linspace(y1, y2, yEle + 1)
    z = linspace(z2, z1, zEle + 1)
    
    counter = 1;
    for zIter = 1:zEle+1
        for yIter = 1:yEle+1
            for xIter = 1:xEle+1
                fprintf('%.0f,%6.4f,%6.4f,%6.4f\n', counter, x(xIter), y(yIter), z(zIter))
                counter = counter + 1;
                if (counter == 100)
                    return;
                end
            end
        end
    end

end

