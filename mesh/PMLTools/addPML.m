function addPML(nx,ny,nz,thickness,PID,symmetry,infile,outfile)
%The function addPML converts elements within a given range to PML elements
% 
%   Usage:
%   []=addPML(nx,ny,nz,thickness,PID,infile,outfile);
% 
%   OUTPUTS
%           Saves an elements file with given outfile string
%               For Example:
%                           elemsPML.dyn
%   INPUTS                 
%           nx (int)- Number of elements in X dimension of rectangular mesh.
%           ny (int)- Number of elements in Y dimension of rectangular mesh.
%           nz (int)- Number of elements in Z dimension of rectangular mesh.
%
%           thickness (int, 5-10)- Thickness of the PML layer to be
%           created. See NOTE A for more details.
%
%           PID (int)- New LS-DYNA PART ID that will be assigned to the
%           PML. It is important to use the same ID in the DYNA deck
%           for assigning a MATERIAL ID to this PART ID.
%
%           symmetry (char 'q', 'h', 'n') - flag to choose quarter, half or
%           no symmetry.
%
%           infile (string) - File name of your input elements file,          
%           ('elems.dyn' or similar)
%
%           outfile (string) - Output file name for the updated
%           elements file ('elemsPML.dyn' or similar)
%
%       Example Usage (for included Test Mesh):
%                       addPML(32,20,160,5,3,'q','elems.dyn','elemStr.dyn')
%
%   NOTE A - PML Thickness
%           
%           It is suggested in the LS-DYNA Manual for PMLs to be between 5
%           & 10 elements thick depending on the application. See the DYNA
%           manual VOL. 2 MAT_230 (in the (visco)elastic case).
%
%   NOTE B - Nodal Constraints
%
%           It is noted in the LS-DYNA Manual that nodes on the outside of
%           a PML must be constrained. This script does not accomplish this
%           task automatically. Use the script pmlNodeConstaint to
%           constrain nodes
%
%   Author CJM - 5/5/2014
%   Update CJM - Added notes - 8/27/2014
%
%           See also pmlNodeConstraints, readElemFile, readNodeFile,
%           writeElemFile, writeNodeFile


%Parameters for Included Test Mesh

% nx=20;
% ny=32;
% nz=160;
% thickness=5;
% PML=3;

if symmetry=='q' || symmetry=='h' || symmetry =='n'
else
    disp('Not a valid symmetry case: Returning');
end
if thickness > 10 || thickness < 5
    warning('Thicknesses for PMLs should be between 5 - 10 elements. See DYNA Materials Manual @ MAT_230 for confirmation');
end

PML=PID;
larea=nx*ny;                        %Area (NumElements) of each layer of mesh.
elems=readElemFile(infile);    %Sub function to read in elems as a Nx10 matrix


%First, calculate the area of the bottom of the mesh and make the first
%(5-10) layers into a PML. You should check the adj. element to the PML to
%make sure that you are matching each to the correct material (Or use the
%fiber script fiberPhantom, will update in future version).


elems(1:nx*ny*thickness,2)=PML;             %Bottom PML
elems(end-(larea*thickness)+1:end,2)=PML;     %Top PML  


%Now we need to see what symmetry case we have in order to set the edges of
%the mesh as the correct PML.
  switch symmetry
      
% Quarter Symmetry

      case 'q'
          
        for i=thickness+1:nz-thickness
            for j=1:thickness*nx
                elems((larea*i)-thickness*nx+j,2)=PML; %Outer X Face is changed to PML
            end
        end
        
        for i=thickness:nz-thickness-1
            for j=0:ny 
                for k=1:thickness
                    elems(larea*i+k+(nx*j),2)=PML;          %Outer Y Face is changed to PML
                end
            end
        end

%Now for Half Symmetry
      case 'h'
          
        for i=thickness:nz-thickness-1
            for j=1:thickness*nx
                elems((larea*i)+thickness*nx-j+1,2)=PML; %Inner (- Y direction) X Face is changed to PML
            end
        end
        
        for i=thickness+1:nz-thickness
            for j=1:thickness*nx
                elems((larea*i)-thickness*nx+j,2)=PML; %Outer X Face is changed to PML
            end
        end
        
        for i=thickness:nz-thickness-1
            for j=0:ny      
                for k=1:thickness
                    elems(larea*i+k+(nx*j),2)=PML;          %Outer Y Face is changed to PML
                end
            end
        end

%No Symmetry
      case 'n'
          
        for i=thickness:nz-thickness-1
            for j=1:thickness*nx
                elems((larea*i)+thickness*nx-j+1,2)=PML; %Inner (- Y direction) X Face is changed to PML
            end
        end

        for i=thickness+1:nz-thickness
            for j=1:thickness*nx
                elems((larea*i)-thickness*nx+j,2)=PML; %Outer X Face is changed to PML
            end
        end

        for i=thickness+1:nz-thickness
            for j=0:ny-1      
                for k=1:thickness
                    elems(larea*i-k-(nx*j)+1,2)=PML;          %Inner Y Face is changed to PML
                end
            end
        end

        for i=thickness:nz-thickness-1
            for j=0:ny      
                for k=1:thickness
                    elems(larea*i+k+(nx*j),2)=PML;          %Outer Y Face is changed to PML
                end
            end
        end
  end
writeElemFile(outfile,elems);

    


