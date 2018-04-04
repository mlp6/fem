#include <stdio.h>
#include "field.h"

main()
{
struct FieldParams params;

	params.impulse = "gaussian";
	params.frequency = 7.2;
	params.samplingFrequency = 100E6;

	fprintf(stderr, "sampling %d\n", params.samplingFrequency);

	dynaField(params, 1, 0);
}
