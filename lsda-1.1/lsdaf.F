c
c Need to insert #define statements here for "Offset" if it
c corresponds to anything other than an integer.  It is "unsigned long"
c in the I/O routines, which is "integer" for most machines but may
c be otherwise for some??
c
#if defined ALPHA || defined SGI64 || defined ADDR64 || defined CRAY
#  define Offset integer*8
#else
#  define Offset integer
#endif
#if defined AUTODOUBLE && defined MPP
#  if defined IBMAIX43 || defined HPUX
#    undef Offset
#    define Offset integer*4
#  endif
#endif
c
c Length is also unsigned long at the moment, so whatever works
c for Offset should work for Length....
#ifndef Length
#  define Length Offset
#endif
      integer function lsdaopen(filen, mode,ierr)
      implicit none
c
      character*(*) filen
      integer mode,ierr
c
      character*1024 lfilen
      integer ifilen
      equivalence (lfilen,ifilen)
      integer i
      integer lsda_open_c
      external lsda_open_c
      integer nbleng
      external nbleng
c
      i=nbleng(filen)
      if (i.eq.0) then
        lsdaopen=-1
        return
      endif
c
      lfilen = filen(1:i)//char(0)
      lsdaopen = lsda_open_c(ifilen,mode,ierr)
c
      return
      end
c
      integer function lsdareopen(filen, filenum, offset,ierr)
      implicit none
c
      character*(*) filen
      integer filenum,ierr
      integer ifilen
      equivalence (lfilen,ifilen)
      integer offset
c
      Offset loffset
      character*1024 lfilen
      integer i
      integer lsda_reopen_c
      external lsda_reopen_c
      integer nbleng
      external nbleng
c
      i=nbleng(filen)
      if (i.eq.0) then
        lsdareopen = -1
        return
      endif
c
      lfilen = filen(1:i)//char(0)
      loffset = offset
      lsdareopen = lsda_reopen_c(ifilen,filenum,loffset,ierr)
c
      return
      end
c
      integer function lsdafopen(filen, filenum, offset, handle, ierr)
      implicit none
c
      character*(*) filen
      integer filenum,handle,ierr
      integer ifilen
      equivalence (lfilen,ifilen)
      integer offset
c
      Offset loffset
      character*1024 lfilen
      integer i
      integer lsda_fopen_c
      external lsda_fopen_c
      integer nbleng
      external nbleng
c
      i=nbleng(filen)
      if (i.eq.0) then
        lsdafopen = -1
        return
      endif
      lfilen = filen(1:i)//char(0)
      loffset = offset
      lsdafopen = lsda_fopen_c(ifilen,filenum,loffset,handle,ierr)
c
      return
      end
c
      integer function lsdafsize(handle,ierr)
      implicit none
c
      integer handle,ierr
c
      Length lsda_fsize_c
      external lsda_fsize_c
c
      lsdafsize = lsda_fsize_c(handle,ierr)
      return
      end
c
      subroutine lsdacd(handle, path,ierr)
      implicit none
c
      integer handle,ierr
      character*(*) path
c
      character*1024 lpath
      integer ipath
      equivalence (lpath,ipath)
      integer i
      integer nbleng
      external nbleng
c
      i=nbleng(path)
      if (i.eq.0) return
      lpath = path(1:i)//char(0)
      call lsda_cd_c(handle,ipath,ierr)
c
      return
      end
c
      subroutine lsdawrite(handle, typeid, name, length, data,
     & ierr)
      implicit none
c
      integer handle,typeid,length,data(*),ierr
      character*(*) name
c
      character*1024 lname
      integer iname
      equivalence (lname,iname)
      integer i
      integer nbleng
      external nbleng
c
      i=nbleng(name)
      lname = name(1:i)//char(0)
      call lsda_write_c(handle,typeid,iname,length,data,ierr)
c
      return
      end
c
      subroutine lsdaread(handle, typeid, name, offset, 
     & number, data, ierr)
      implicit none
c
      integer handle,typeid,offset,number,data(*),ierr
      character*(*) name
c
      character*1024 lname
      integer iname
      equivalence (lname,iname)
      integer i
      integer nbleng
      external nbleng
c
      i=nbleng(name)
      lname = name(1:i)//char(0)
      call lsda_read_c(handle,typeid,iname,offset,number,
     & data,ierr)
c
      return
      end
c
      subroutine lsdagetname(handle, name, length, ierr)
      implicit none
c
      integer handle,length,ierr
      character*(*) name
c
      character*1024 lname
      integer iname
      equivalence (lname,iname)
c
      call lsda_getname_c(handle,iname,length,ierr)
      name = lname(1:length)
c
      return
      end
c
      subroutine lsdagetbasename(handle, name, length, ierr)
      implicit none
c
      integer handle,length,ierr
      character*(*) name
c
      character*1024 lname
      integer iname
      equivalence (lname,iname)
c
      call lsda_getbasename_c(handle,iname,length,ierr)
      name = lname(1:length)
c
      return
      end
c
      integer function lsdagethandle(filen, ierr)
      implicit none
c
      integer ierr
      character*(*) filen
c
      character*1024 lfilen
      integer ifilen
      equivalence (lfilen,ifilen)
      integer i
      integer lsda_gethandle_c
      external lsda_gethandle_c
      integer nbleng
      external nbleng
c
      i=nbleng(filen)
      if (i.eq.0) then
        lsdagethandle = -1
        return
      endif
c
      lfilen = filen(1:i)//char(0)
      lsdagethandle = lsda_gethandle_c(ifilen,ierr)
c
      return
      end
c
      subroutine lsdaqueryvar(handle, name, type, length, filenum,
     &  ierr)
      implicit none
c
      integer handle,type,length,filenum,ierr
      character*(*) name
c
      character*1024 lname
      integer iname
      equivalence (lname,iname)
      integer i
      integer nbleng
      external nbleng
c
      i=nbleng(name)
      lname = name(1:i)//char(0)
      call lsda_queryvar_c(handle,iname,type,length,filenum,ierr)
c
      return
      end
c
      integer function lsdaopendir(handle,name,ierr)
      implicit none
c
      integer handle,ierr
      character*(*) name
      integer lsda_opendir_c
      external lsda_opendir_c
      integer nbleng
      external nbleng
c
      character*1024 lname
      integer iname
      equivalence (lname,iname)
      integer i
c
      i=nbleng(name)
      lname = name(1:i)//char(0)
      lsdaopendir= lsda_opendir_c(handle,iname,ierr)
c
      return
      end
c
      subroutine lsdareaddir(dir,name,typeid,len,filenum,ierr)
      implicit none
c
      integer dir,typeid,len,filenum,ierr
      character*(*) name
c
      character*1024 lname
      integer iname
      equivalence (lname,iname)
      integer namelen
c
      call lsda_readdir_c(dir,iname,namelen,typeid,len,filenum,ierr)
c
      name = lname(1:namelen)
      return
      end
c
      integer function nbleng(name)
      implicit none
c
c Find non-blank length of string
c
      character*(*) name
      integer i,slen
c
      slen=len(name)
      do i=slen,1,-1
        if(name(i:i).ne.' ') then
          nbleng = i
          return
        endif
      enddo
      nbleng = 0
      return
      end
