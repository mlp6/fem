ANACONDA3  = $(HOME)/miniconda3
CC         = gcc
CFLAGS     = -c -fpic
LD         = ld -shared
SRCS       = create_disp_dat.c create_disp_dat_wrap.c
INTERFACE  = create_disp_dat.i
OBJS       = create_disp_dat.o create_disp_dat_wrap.o
TARGET     = _create_disp_dat.so
PYTHON_INCLUDE    = -I$(ANACONDA3)/envs/fem/include/python3.6m
PYTHON_LIB = -L$(ANACONDA3)/lib -lpython3.6m
SWIG       = swig

SWIGOPT     = -python

all: create_disp_dat _create_disp_dat.so

_create_disp_dat.so: $(SRCS) $(INTERFACE)
	$(SWIG) $(SWIGOPT) $(INTERFACE)
	$(CC) $(CFLAGS) $(PYTHON_INCLUDE) $(SRCS)
	$(LD) $(OBJS) -o $(TARGET)


create_disp_dat: create_disp_dat.c
	gcc -o create_disp_dat create_disp_dat.c

test: create_disp_dat
	./create_disp_dat -i testing/nodout1 -o testing/disp.dat
	@cmp testing/disp.dat.good testing/disp.dat ; if [ $$? -eq 0 ] ; then echo "passed test" ; else echo "failed test"; fi;
	rm testing/disp.dat

clean:
	rm -f *_wrap* *.o
