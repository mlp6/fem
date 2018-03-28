#include "field.h"

main()
{
struct FieldParams params;

	params.impulse = "gaussian";
	params.frequency = 7.2;
	params.samplingFrequency = 100E6;

	dynaField(params, 1, 0);
}
