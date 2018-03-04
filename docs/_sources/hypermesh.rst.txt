Hypermesh Tutorial
==================

Rectilinear mesh generation using HyperMesh (Douglas Dumont)

Set Global Properties to LS Dyna
--------------------------------

#. Click on the global button in the lower-right.

#. Click the load button beside the template file. Select latest version
   of LS Dyna key.

#. Click return.

Define the Part and Set Material Properties
-------------------------------------------

#. Goto the Collectors Menu.

#. Click on the up arrow beside collector type.

#. Select Mat to define the collector as a material.

#. Enter a name to describe the part

#. Click on card image. Select the desired material card. Use MATL-TH1
   for a thermally isotropic material.

#. Click Create/Edit

#. Enter the properties for the material. For thermal properties, TRO is
   the material density, TGRLC and TGMULT should be zero, HC is the heat
   capacity, and TC is the thermal conductivity for a given material.

#. Return to the main menus.

Uniform Mesh Generation
-----------------------

#. Click on Perf rather than Std besides GFX. This will make mesh
   generation much faster.

#. Goto Geometry, then Create Nodes.Enter four nodes to define one face
   of your mesh. For uniform meshes without biasing, it is suggested to
   define nodes along the x-y plane

#. Goto 2-D and select Planes.

#. Select Nodes in the left drop down menu. Click on Nodes and highlight
   the nodes you are interested in defining a plane for.

#. Select surface-only in the right drop down menu.

#. Select trimmed and then click on Create.

#. Go back to the 2-D menu and select Automesh.

#. Click on the surface. It should turn from red to white.

#. Click on mesh, making sure interactive mesh is highlighted.

#. Numbers will now appear along the sides of the surface. Selecting
   these allow defining the number of elements along that
   edge.Alternatively, enter the desired element density into elem
   density and click Set Edge To.

#. Define element densities for all four edges.

#. Click Mesh to generate the mesh. Click Reject to reject a generated
   mesh.

#. Return to the main menu once a suitable mesh has been generated.

#. The two-dimenional mesh now needs to be dragged to generate a 3-D
   volume. For example, a planar mesh can be generated at the face of
   the transducer and then grown along the z axis to make the model
   volume.

#. Goto 3-D. Goto Drag.

#. Click drag elems.

#. Click elements. Select all.

#. Click on the arrow button beside N1 N2 N3.

#. Select the direction to drag the mesh in under to create a volume.
   For a mesh defined in the x-y plane, the z direction should be
   specified.

#. Enter the distance to drag the mesh.

#. On Drag defines the element density in the dragged direction. Enter
   the desired element density.

#. Select Drag+ to drag elements in the + direction. Select Drag - for
   the reverse.

#. To view the mesh, click on View, then select Iso1.

#. Click return.

#. Sections with different densities can be generated in a similar
   fashion. First create a plane divided into subsections depending on
   the number of desired densities. Use Automesh to specify the desired
   number of edge elements for each section. Create the planar mesh and
   drag this new mesh to create a volume.

Removing unneeded nodes and surfaces
------------------------------------

#. The volume is almost finished. Now the nodes and surfaces created
   earlier should be deleted. To do this, click on Display and turn
   Elems off. Only the initial nodes and surfaces will now be displayed.

#. Goto Geom

#. Goto Temp Nodes

#. Click nodes and select all.

#. Select clear.

#. To remove the surface, goto Tools and then Delete.

#. Select Surfs and click on the surfaces to delete. Select Delete
   entity.

#. To check the number of elements and nodes, goto Tools and then Count.
   Select all.

#. Your mesh is almost finished. To write to a ls-dyna file, goto Files
   and then select Export.

#. Make sure the dyna key is selected and click write as. Enter a file
   name and click Save.

#. Open the saved .dyn file in your favorite text editor. Search for
   Shell. This section of the dyna deck defines shell elements generated
   from the 2-D automesh command. We only want solid elements. Delete
   all the nodes under Shell elements.

#. Enter the desired control cards into deck.

#. Drink a beer. Watch a movie. Work from home. Your mesh is now
   finished.

HyperMesh Alternatives
======================

Commercial HyperMesh is not cheap, so there are some other considerations:

#. HyperMesh Student Edition (restricted to 1 computer; no direct ls-dyna export)
#. LS-PREPOST
#. http://geuz.org/gmsh/
#. http://www.vmtk.org/
#. http://febio.org/preview/
#. http://sourceforge.net/projects/netgen-mesher/
#. http://wias-berlin.de/software/tetgen/

Keep in mind that tetrahedral elements are not well conditioned for
nearly-incompressible materials, so most of these are not ideal options.
