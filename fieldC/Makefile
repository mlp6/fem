INCLUDE=.
#FIELD_INCLUDE=/aiki/scratch/ndd/Field_II_Pro-master/c_library
FIELD_INCLUDE=/work/ndd/Field_II_Pro-master/c_library

CFLAGS=

OS=$(shell lsb_release -si)
ifeq ($(OS),Ubuntu)
	CFLAGS=-no-pie
endif

main: checkOnAxis.o checkUniform.o correctAxialLens.o dynaField.o dynaWrite.o field2dyna.o gaussPulse.o readMpn.o main.c
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) checkOnAxis.o checkUniform.o correctAxialLens.o dynaField.o dynaWrite.o field2dyna.o gaussPulse.o readMpn.o main.c cJSON.c $(FIELD_INCLUDE)/lib_Field_II.a -lpthread -lm

checkOnAxis.o: checkOnAxis.c field.h
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c checkOnAxis.c

checkUniform.o: checkUniform.c field.h
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c checkUniform.c

correctAxialLens.o: correctAxialLens.c field.h
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c correctAxialLens.c

dynaField.o: dynaField.c cJSON.c cJSON.h field.h
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c dynaField.c cJSON.c

dynaWrite.o: dynaWrite.c field.h
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c dynaWrite.c

dynaTest.o: dynaTest.c
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c dynaTest.c

dynaTest: dynaTest.o dynaField.o cJSON.o gaussPulse.o readMpn.o
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) dynaTest.o dynaField.o cJSON.o gaussPulse.o readMpn.o -o dynaTest $(FIELD_INCLUDE)/lib_Field_II.a -lpthread -lm

field2dyna.o: field2dyna.c field.h
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c field2dyna.c

readMpn.o: readMpn.c
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c readMpn.c

gaussTest: gaussTest.o gaussPulse.o
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) gaussTest.o gaussPulse.o -o gaussTest $(FIELD_INCLUDE)/lib_Field_II.a -lpthread -lm

gaussTest.o: gaussTest.c
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c gaussTest.c

gaussPulse.o: gaussPulse.c field.h
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c gaussPulse.c

testFieldConversion.o: testFieldConversion.c
	cc $(CFLAGS) -c -I $(INCLUDE) -I $(FIELD_INCLUDE) testFieldConversion.c

testFieldConversion: testFieldConversion.o checkOnAxis.o checkUniform.o readMpn.o
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) testFieldConversion.o checkOnAxis.o checkUniform.o readMpn.o -o testFieldConversion

uniformTest.o: uniformTest.c
	cc $(CFLAGS) -I $(INCLUDE) -I $(FIELD_INCLUDE) -c uniformTest.c -lm

uniformTest: uniformTest.o checkUniform.o readMpn.o
	cc $(CFLAGS) -I $(INCLUDE) uniformTest.o checkUniform.o readMpn.o -o uniformTest

clean:
	rm *.o a.out
