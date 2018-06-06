/*
 * the routine 'checkUniform' checks for a uniform mesh
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "field.h"

typedef struct node {
	double value;
	struct node *nextEntry;
	} node;

/* produce a sorted list of the unique mesh points */

node
*insertSortedUnique(node *head, double num)
{
node *temp, *prev, *next;

	if ((temp = (node *)malloc(sizeof(node))) == NULL) {
		return(NULL);
		}

	temp->value = num;
	temp->nextEntry = NULL;

	if (!head) {
		head = temp;
		}
	 else{
		prev = NULL;
		next = head;
		while (next && next->value <= num) {
			if (next->value == num) {
				free(temp);
				return(head);
				}
			prev = next;
			next = next->nextEntry;
			}
		if (!next) {
			prev->nextEntry = temp;
			}
		 else{
			if (prev) {
				temp->nextEntry = prev->nextEntry;
				prev->nextEntry = temp;
				}
			 else {
				temp->nextEntry = head;
				head = temp;
				}            
			}   
		}

	return head;
}

void free_list(node *head)
{
	node *prev = head;
	node *cur = head;
	while (cur) {
		prev = cur;
		cur = prev->nextEntry;
		free(prev);
		}       
}

/*
 * the routine 'checkUniform' does the following:
 *
 * find all the unique x, y and z coordinates
 *
 * x = unique(measurementPoints(:, 1));
 * y = unique(measurementPoints(:, 2));
 * z = unique(measurementPoints(:, 3));
 *
 * take the difference of each adjacent pair of {xyz}, divide by the difference
 * between the first two coordinates in each dimension, subtract 1 from that
 * ratio, check to see if that is less than 10^-9, then take the absolute value
 * of that test.
 *
 * if all the comparisons for each of x, y and z are less than 10^-9, the mesh
 * is linear.
 */

int
checkUniform(struct nodeEntry *pointsAndNodes, int numNodes, int debug)
{
int i;
int uniqueXpnts = 0, uniqueYpnts = 0, uniqueZpnts = 0;
double xSecondLessFirst, ySecondLessFirst, zSecondLessFirst;
double *xDiffs, *yDiffs, *zDiffs;
node *headX, *headY, *headZ, *p;

	headX = NULL;
	headY = NULL;
	headZ = NULL;

	for (i = 0; i < numNodes; i++) {
		headX = insertSortedUnique(headX, pointsAndNodes[i].x);
		headY = insertSortedUnique(headY, pointsAndNodes[i].y);
		headZ = insertSortedUnique(headZ, pointsAndNodes[i].z);
		if ((headX == NULL) || (headY == NULL) || (headZ == NULL)) {
			fprintf(stderr, "couldn't allocate space for sort node\n");
			return(-1);
			}
		}

	p = headX;
	if (debug) fprintf(stderr, "\nThe X numbers are:\n");

	while (p != NULL) {
		if (debug) fprintf(stderr, "%f\n", p->value);
		uniqueXpnts++;
		p = p->nextEntry;
		}

	if (debug) fprintf(stderr, "unique X points %d\n", uniqueXpnts);

	p = headY;
	if (debug) fprintf(stderr, "\nThe Y numbers are:\n");

	while (p != NULL) {
		if (debug) fprintf(stderr, "%f\n", p->value);
		uniqueYpnts++;
		p = p->nextEntry;
		}

	if (debug) fprintf(stderr, "unique Y points %d\n", uniqueYpnts);

	p = headZ;
	if (debug) fprintf(stderr, "\nThe Z numbers are:\n");

	while (p != NULL) {
		if (debug) fprintf(stderr, "%f\n", p->value);
		uniqueZpnts++;
		p = p->nextEntry;
		}

	if (debug) fprintf(stderr, "unique Z points %d\n", uniqueZpnts);

	xDiffs = (double *)malloc(sizeof(double) * (uniqueXpnts - 1));

	p = headX;

	i = 0;

	while (p != NULL) {
		if (p->nextEntry != NULL) {
			xDiffs[i] = (p->nextEntry)->value - p->value;
			if (i == 0) xSecondLessFirst = xDiffs[i];
			if (debug) fprintf(stderr, "x 2 - 1 %f\n", xDiffs[i]);
			i++;
			}
		p = p->nextEntry;
		}

	yDiffs = (double *)malloc(sizeof(double) * (uniqueXpnts - 1));

	p = headY;

	i = 0;

	while (p != NULL) {
		if (p->nextEntry != NULL) {
			yDiffs[i] = (p->nextEntry)->value - p->value;
			if (i == 0) ySecondLessFirst = yDiffs[i];
			if (debug) fprintf(stderr, "y 2 - 1 %f\n", yDiffs[i]);
			i++;
			}
		p = p->nextEntry;
		}

	zDiffs = (double *)malloc(sizeof(double) * (uniqueXpnts - 1));

	p = headZ;

	i = 0;

	while (p != NULL) {
		if (p->nextEntry != NULL) {
			zDiffs[i] = (p->nextEntry)->value - p->value;
			if (i == 0) zSecondLessFirst = zDiffs[i];
			if (debug) fprintf(stderr, "z 2 - 1 %f\n", zDiffs[i]);
			i++;
			}
		p = p->nextEntry;
		}

/* if any of the diffs aren't less than 10E-9 the mesh isn't uniform */

	for (i = 0; i < uniqueXpnts - 1; i++) {
		if (debug) fprintf(stderr, "testing %f %f %f ratio %f\n", xDiffs[i],
			xSecondLessFirst, xDiffs[i] / xSecondLessFirst,
			fabs((xDiffs[i] / xSecondLessFirst) - 1));
		if (fabs((xDiffs[i] / xSecondLessFirst) - 1) > 10E-9) return(0);
		}

	for (i = 0; i < uniqueYpnts - 1; i++) {
		if (debug) fprintf(stderr, "testing %f %f %f ratio %f\n", yDiffs[i],
			ySecondLessFirst, yDiffs[i] / ySecondLessFirst,
			fabs((xDiffs[i] / xSecondLessFirst) - 1));
		if (fabs((yDiffs[i] / ySecondLessFirst) - 1) > 10E-9) return(0);
		}

	for (i = 0; i < uniqueZpnts - 1; i++) {
		if (debug) fprintf(stderr, "testing %f %f %f ratio %f\n", zDiffs[i],
			zSecondLessFirst, zDiffs[i] / zSecondLessFirst,
			fabs((xDiffs[i] / xSecondLessFirst) - 1));
		if (fabs((zDiffs[i] / zSecondLessFirst) - 1) > 10E-9) return(0);
		}

	free_list(headX);
	free_list(headY);
	free_list(headZ);

	return(1);
}
