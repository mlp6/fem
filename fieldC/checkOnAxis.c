#include "field.h"

int
checkOnAxis(struct nodeEntry *pointsAndNodes, int numNodes)
{
int i, found = 0;

	for (i = 0; i < numNodes; i++)
		if (pointsAndNodes[i].x == 0 && pointsAndNodes[i].y == 0) {
			found = 1;
			break;
			}

	return(found);
}
