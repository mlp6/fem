all: create_disp_dat

create_disp_dat:
	g++ scale_disp_dat.cpp -o scale_disp_dat

test: create_disp_dat
	./create_disp_dat -i testing/nodout1 -o testing/disp.dat
	@cmp testing/disp.dat.good testing/disp.dat ; if [ $$? -eq 0 ] ; then echo "passed test" ; else echo "failed test"; fi;
	rm testing/disp.dat

clean:
	rm -f *_wrap* *.o
