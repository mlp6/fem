
#include "field.h"

main()
{
struct FieldParams params;

	params.impulse = "gaussian";
	params.samplingFrequency = 100E6;

	gaussPulse(0.5, 1000.0, params);
}
