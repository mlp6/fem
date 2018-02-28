function savevtkvector(X, Y, Z, filename)
%  savevtkvector Save a 3-D vector array in VTK format
%  savevtkvector(X,Y,Z,filename) saves a 3-D vector of any size to
%  filename in VTK format. X, Y and Z should be arrays of the same
%  size, each storing speeds in the a single Cartesian directions.
    if ((size(X) ~= size(Y)) | (size(X) ~= size(Z)))
        fprint('Error: velocity arrays of unequal size\n'); return;
    end
    [nx, ny, nz] = size(X);
    fid = fopen(filename, 'wt');
    fprintf(fid, '# vtk DataFile Version 2.0\n');
    fprintf(fid, 'Comment goes here\n');
    fprintf(fid, 'ASCII\n');
    fprintf(fid, '\n');
    fprintf(fid, 'DATASET STRUCTURED_POINTS\n');
    fprintf(fid, 'DIMENSIONS    %d   %d   %d\n', nx, ny, nz);
    fprintf(fid, '\n');
    fprintf(fid, 'ORIGIN    0.000   0.000   0.000\n');
    fprintf(fid, 'SPACING    1.000   1.000   1.000\n');
    fprintf(fid, '\n');
    fprintf(fid, 'POINT_DATA   %d\n', nx*ny*nz);
    fprintf(fid, 'VECTORS vectors float\n');
    fprintf(fid, '\n');
    for a=1:nx
        for b=1:ny
            for c=1:nz
                fprintf(fid, '%f ', X(a,b,c));
                fprintf(fid, '%f ', Y(a,b,c));
                fprintf(fid, '%f ', Z(a,b,c));
            end
            fprintf(fid, '\n');
        end
    end
    fclose(fid);
return
