# User-Defined Materials

Based on an email from support@lstc.com (Todd Slavic):   

In addition to Appendix A in the User's Manual (www.lstc.com/download/manuals), please  see the supplemental notes in   

http://ftp.lstc.com/anonymous/outgoing/jday/faq/user\_defined\_materials.faq   

Here, basically, are the steps to get started:   

1. You need the object files from LSTC that matches your system. These  files comes in a package that also includes a Makefile and Fortran  files. The file dyn21.f is the file that has the Fortran coding in it.  The routines for the user materials are umat41-50 / umat41v-50v and in  one of these routines, you place your own code, being careful not to  alter the argument list.   

2. You need to have a compiler that matches the compiler used for these  object files - this information is in the README\_first file for each  release. This file is found that user ftp site where you download the QA  tested LS-DYNA executable.   

The exception is if you use a package with the word "sharelib" in the name,  in which case any compiler should work. I believe this option is only  for MPP and only for a few platforms.   

3. You compile the executable using the Makefile that came with the  package.   

4. You should now have your own executable that has this material model  included. The use of this material model is invoked in the keyword deck  by the keyword command `*MAT_USER_DEFINED_MATERIAL_MODELS` (`*MAT_041` to `*MAT_050`).   

I suggest that before you implement your own model in the `dyn21.f` file  (step 1 above), you try to compile withOUT changing any of the source code provided.  Then you know if the compiler and setup works. When that is ok, you can move to  implement your own code.   

5. Download the object files from: http://ftp.lstc.com/objects/   

6. For an example of a complete user-defined material subroutine, see subroutine `umat41` in `dyn21.f`. This user-defined material behaves like `*mat_elastic` but is called via `*mat_user_defined_material_models` with `MT` set to `41`. An example input deck is: http://ftp.lstc.com/anonymous/outgoing/jday/2x_sphere2plate.k.gz   

Please know that officially LSTC doesn't provide technical support for debugging of user-defined materials  or other user-defined subroutines, but unofficially we do our best to provide help, as our workload permits.
