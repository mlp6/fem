      integer lsdaopen
      integer lsdafopen
      integer lsdaresume
      integer lsdafsize
      integer lsdanextopen
      integer lsdanewpattern
      integer lsdasetpattern
      integer lsdagethandle
      integer lsdaopendir
c
c     external lsdaopen
c     external lsdafopen
c     external lsdaresume
c     external lsdafsize
c     external lsdanextopen
c     external lsdanewpattern
c     external lsdasetpattern
c     external lsdagethandle
c
      integer LSDA_READONLY
      integer LSDA_WRITEONLY
      integer LSDA_SUCCESS
      parameter (LSDA_READONLY = 0)
      parameter (LSDA_WRITEONLY = 1)
      parameter (LSDA_SUCCESS = 0)
c
      integer LSDA_I1    
      integer LSDA_I2    
      integer LSDA_I4    
      integer LSDA_I8    
      integer LSDA_U1    
      integer LSDA_U2     
      integer LSDA_U4 
      integer LSDA_U8  
      integer LSDA_R4   
      integer LSDA_R8    
      integer LSDA_INT   
      integer LSDA_SHORT 
      integer LSDA_LONG  
      integer LSDA_UINT  
      integer LSDA_USHORT
      integer LSDA_ULONG 
      integer LSDA_FLOAT 
      integer LSDA_DOUBLE 
      integer LSDA_INTEGER
      integer LSDA_REAL 
      integer LSDA_DP
      parameter (LSDA_I1     = 1)
      parameter (LSDA_I2     = 2)
      parameter (LSDA_I4     = 3)
      parameter (LSDA_I8     = 4)
      parameter (LSDA_U1     = 5)
      parameter (LSDA_U2     = 6)
      parameter (LSDA_U4     = 7)
      parameter (LSDA_U8     = 8)
      parameter (LSDA_R4     = 9)
      parameter (LSDA_R8     =10)
      parameter (LSDA_INT    =11)
      parameter (LSDA_SHORT  =12)
      parameter (LSDA_LONG   =13)
      parameter (LSDA_UINT   =14)
      parameter (LSDA_USHORT =15)
      parameter (LSDA_ULONG  =16)
      parameter (LSDA_FLOAT  =17)
      parameter (LSDA_DOUBLE =18)
      parameter (LSDA_INTEGER=19)
      parameter (LSDA_REAL   =20)
      parameter (LSDA_DP     =21)
