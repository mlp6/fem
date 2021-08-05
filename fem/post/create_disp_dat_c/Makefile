all: create_disp_dat _create_disp_dat.so

_create_disp_dat.so: create_disp_dat.c create_disp_dat.i
	swig -python create_disp_dat.i
	gcc -O2 -fPIC -c -I/usr/include/python3.9 create_disp_dat.c create_disp_dat_wrap.c
	gcc -shared create_disp_dat.o create_disp_dat_wrap.o -o create_disp_dat.so


create_disp_dat: create_disp_dat.c
	gcc -o create_disp_dat create_disp_dat.c

test: create_disp_dat
	./create_disp_dat -i testing/nodout1 -o testing/disp.dat
	@cmp testing/disp.dat.good testing/disp.dat ; if [ $$? -eq 0 ] ; then echo "passed test" ; else echo "failed test"; fi;
	rm testing/disp.dat

clean:
	rm -f *_wrap* *.o
