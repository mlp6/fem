INCLUDE=.
FIELD_INCLUDE=/aiki/scratch/ndd/Field_II_Pro-master/c_library

main: checkOnAxis.o dynaField.o field2dyna.o gaussPulse.o readMpn.o main.c
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) checkOnAxis.o dynaField.o field2dyna.o gaussPulse.o readMpn.o main.c cJSON.c /aiki/scratch/ndd/Field_II_Pro-master/c_library/lib_Field_II.a -lpthread -lm

checkOnAxis.o: checkOnAxis.c field.h
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) -c checkOnAxis.c

defineImpulseResponse.o: defineImpulseResponse.c field.h
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) -c defineImpulseResponse.c

dynaField.o: dynaField.c cJSON.c cJSON.h field.h
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) -c dynaField.c cJSON.c

dynaTest.o: dynaTest.c
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) -c dynaTest.c

dynaTest: dynaTest.o dynaField.o cJSON.o gaussPulse.o readMpn.o
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) dynaTest.o dynaField.o cJSON.o gaussPulse.o readMpn.o -o dynaTest /aiki/scratch/ndd/Field_II_Pro-master/c_library/lib_Field_II.a -lpthread -lm

field2dyna.o: field2dyna.c field.h
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) -c field2dyna.c

readMpn.o: readMpn.c
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) -c readMpn.c

gaussTest: gaussTest.o defineImpulseResponse.o gaussPulse.o
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) gaussTest.o defineImpulseResponse.o gaussPulse.o -o gaussTest -lm

gaussTest.o: gaussTest.c
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) -c gaussTest.c

gaussPulse.o: gaussPulse.c field.h
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) -c gaussPulse.c

testFieldConversion.o: testFieldConversion.c
	cc -c -I $(INCLUDE) -I $(FIELD_INCLUDE) testFieldConversion.c

testFieldConversion: testFieldConversion.o checkOnAxis.o readMpn.o
	cc -I $(INCLUDE) -I $(FIELD_INCLUDE) testFieldConversion.o checkOnAxis.o readMpn.o -o testFieldConversion
