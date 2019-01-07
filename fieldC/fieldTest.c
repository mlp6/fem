#include <stdio.h>
#include "field.h"		/* includes field_II.h */

main()
{
sys_con_type   *sys_con;      /*  System constants for Field II */ 
point_type focus;

	focus.x = 1;
	focus.y = 1;
	focus.z = 1;

	xdc_focused_array(64, 7.7E-6, .005, 1.54E-6, .04, 2, 2, focus);
}
