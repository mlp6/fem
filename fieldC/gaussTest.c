
#include "field.h"

sys_con_type   *sys_con;      /*  System constants for Field II */

main()
{
struct FieldParams params;
double fBW, fc;

	params.impulse = "gaussian";
	params.samplingFrequency = 100E6;

	fBW = 0.7;
	fc = 3000000.0;

	sys_con = field_init(-1);

/* 	defineImpulseResponse(0.7, 3000000.0, params); */
	gaussPulse(fBW, fc, params, 1);
}
