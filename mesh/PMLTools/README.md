PML Tools
=========
Start by reading the help from the function ```addPML```. That will describe
what happens on a basic level. For an example on how to use add a PML to an
existing mesh, try out the ```makePMLhelper``` function.

A test mesh is inclued with the toolkit. You can parse the elements and nodes
or use the provided files to add a PML. Open ```TestCard.dyn``` to see the
output of the example script.

The inputs for the test mesh should be as follows:

```
nx=20;
ny=32;
nz=160;
PMLthickness=5;
PID=3;
symmetry='q';
nodein='nodes.dyn';
elemin='elems.dyn';
elemout='elemStr.dyn';
```

Contributers
============
 * Mallory Selzo (UNC-CH)
 * Chris Moore (UNC-CH)
    christopher_j_moore@med.unc.edu
    chrisjmoore@unc.edu
    cjm69@duke.edu
    cjmoore3@ncsu.edu
 * Modified: Mark Palmeri (mlp6@duke.edu)

