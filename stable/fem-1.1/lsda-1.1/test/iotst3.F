      program test
      implicit none
c
      include 'lsda.inc'
c
      integer handle,data(10),i,ierr,icnt
      integer type,length,filenum
      character*32 name
c
      handle = lsdaopen('fdata',LSDA_WRITEONLY,ierr)
c
      do i=1,10
        data(i)=i-1
      enddo
      call lsdacd(handle,'/dir1',ierr)
      call lsdawrite(handle,LSDA_INTEGER,'data0',10,data,ierr)
      do i=1,10
        data(i)=100+i-1
      enddo
      call lsdacd(handle,'/dir2',ierr)
      call lsdawrite(handle,LSDA_INTEGER,'data100',10,data,ierr)
      do i=1,10
        data(i)=200+i-1
      enddo
      call lsdawrite(handle,LSDA_INTEGER,'data200',10,data,ierr)
      call lsdacd(handle,'/dir1/sub1',ierr)
      call lsdacd(handle,'/dir1/sub1/sub2',ierr)
      call lsdawrite(handle,LSDA_INTEGER,'data200',10,data,ierr)
      call lsdaflush(handle,ierr)
      call lsdawrite(handle,LSDA_INTEGER,'data201',10,data,ierr)
      call lsdacd(handle,'/dir1/sub1',ierr)
      call lsdawrite(handle,LSDA_INTEGER,'data201',10,data,ierr)
      call lsdacd(handle,'/dir1/sub2',ierr)
      call lsdawrite(handle,LSDA_INTEGER,'data202',10,data,ierr)
      call lsdanextfile(handle,ierr)
      call lsdacd(handle,'/dir1/sub1',ierr)
      call lsdawrite(handle,LSDA_INTEGER,'data20a',10,data,ierr)
      call lsdacd(handle,'/dir1/sub2',ierr)
      call lsdawrite(handle,LSDA_INTEGER,'data20b',10,data,ierr)
      call lsdaclose(handle,ierr)
      handle = lsdaopen('fdata',LSDA_READONLY,ierr)
      call lsdaqueryvar(handle,'/dir1',type,length,filenum,ierr)
      Print *,'got type=',type
      Print *,'got length=',length
      Print *,'got filenum=',filenum
      Print *,'/dir1 contains:'
      i = lsdaopendir(handle,"/dir1",ierr)
 100  call lsdareaddir(i,name,type,length,filenum,ierr)
      if(type.ge.0)then
         Print *,name(1:10),type,length,filenum
         goto 100
      endif
      Print *,'closing dir'
      call lsdaclosedir(i,ierr)
      Print *,'closing file'
      call lsdaclose(handle,ierr)
      Print *,'done'
      end
