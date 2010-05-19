.SUFFIXES : .o .c .F
BASEDIR=..
vpath
vpath %.F .:$(BASEDIR)
vpath %.c .:$(BASEDIR)
vpath %.h .:$(BASEDIR):$(BASEDIR)/include.lstc
INCDIRS = -I. -I$(BASEDIR) -I$(BASEDIR)/include.lstc
LIBDIRS = -L.

include Makefile.tools

ifeq ($(HAVE_SYSTEM),no)
listem:
	@echo
	@echo Type 'make SYSTEM' where SYSTEM is one of
	@echo
	@echo alpha    = DEC Alpha workstation
	@echo cray     = Cray SV1 system
	@echo fj       = Fujitsu
	@echo hp8      = HP pa8000
	@echo ibmsp    = IBM generic version SINGLE
	@echo linux    = Linux RedHat 6.0 with Portland compiler
	@echo sgi      = SGI R10000
	@echo sun      = SUN Ultra
	@echo
	@echo Type autodouble 'make SYSTEM' where SYSTEM is one of
	@echo
	@echo alphadp  = DEC Alpha workstation
	@echo ibmdp    = IBM pwr3 workstation DOUBLE
	@echo sgidp    = SGI R10000
	@echo hp8dp    = HP pa8000
	@echo
endif

all: ioq tree iotst1 iotst2 iotst3 l2a

l2a: l2a.o liblsda.a
	$(CC) $(CF) -o l2a l2a.o $(LIBDIRS) -llsda
ioq: ioq.o liblsda.a
	$(CC) $(CF) -o ioq ioq.o $(LIBDIRS) -llsda
tree: tree.o liblsda.a
	$(CC) $(CF) -o tree tree.o $(LIBDIRS) -llsda
iotst1: iotst1.o liblsda.a
	$(CC) $(CF) -o iotst1 iotst1.o $(LIBDIRS) -llsda
iotst2: iotst2.o liblsda.a
	$(CC) $(CF) -o iotst2 iotst2.o $(LIBDIRS) -llsda
iotst3: iotst3.o liblsda.a
	$(FC) $(FF) -o iotst3 iotst3.o $(LIBDIRS) -llsda
_force_lib_build:
liblsda.a: _force_lib_build
	- rm liblsda.a
	cd $(BASEDIR); $(MAKE) -f Makefile.module.public "BASEDIR=." \
	"CF=${CF}" "FF=${FF}" "CC=${CC}" "FC=${FC}" "FCTYPE=1"
	ln -s $(BASEDIR)/liblsda.a .
ifeq ($(SYSTEM),pcwin)
	cp $(BASEDIR)/lsda.lib .
endif
clean:
	rm *.o
tar:
	cd ..; rm -rf lsda-1.1; mkdir lsda-1.1; \
        cp --parents lsda.c lsdaf2c.c lsdaf.F lsdatable.c \
	lsdatypes.c btree.c trans.c lsda.h lsda_internal.h btree.h lsda.inc \
        test/ioq.c test/tree.c test/iotst1.c test/iotst2.c test/iotst3.F test/Makefile \
	include.lstc/define.h \
	test/Makefile.tools test/l2a.c test/binascii.txt \
	Makefile.module.public README CHANGES doc/file_format doc/lsda.html \
	lsda-1.1; cd lsda-1.1; uudecode ../license.uu; cd ..; \
        tar -cf lsda-1.1.tar lsda-1.1
.c.o :
	$(CC) -c $(CF) $< $(INCDIRS)
.F.o :
	$(FC) -c $(FF) $< $(INCDIRS)
alpha:
	$(MAKE) SYSTEM=alpha
alphadp:
	$(MAKE) SYSTEM=alphadp
cray:
	$(MAKE) SYSTEM=cray
fj:
	$(MAKE) SYSTEM=fj
hp8:
	$(MAKE) SYSTEM=hp8
hp8dp:
	$(MAKE) SYSTEM=hp8dp
ibmsp:
	$(MAKE) SYSTEM=ibmsp
ibmdp:
	$(MAKE) SYSTEM=ibmdp
linux:
	$(MAKE) SYSTEM=linux
sgi:
	$(MAKE) SYSTEM=sgi
sgidp:
	$(MAKE) SYSTEM=sgidp
sun:
	$(MAKE) SYSTEM=sun
