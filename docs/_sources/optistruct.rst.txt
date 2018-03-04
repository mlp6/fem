OptiStruct Mesh Conversion
==========================

The student version of HyperMesh does not directly export ls-dyna-compatible
input decks, but it does export OptiStruct format.

#. ``OptiStruct_getElemNodes.m`` reads in the geometry from the optistruct file format.
#. ``OptiStruct2DYNA.m`` writes this data to a .k file

The corresponding functions to go the other direction are:
#. ``getElemNodes.m``
#. ``DYNA2OptiStruct.m``

Note that these scripts only migrate the geometry and don't maintain any other
cards (contacts, part definitions, etc) through the conversion.
