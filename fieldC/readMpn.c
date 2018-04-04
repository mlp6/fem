/*
% function [mpn] = readMpn(NodeName)
% 
% Read nodes.dyn and extract points & nodes, skipping the header lines,
% including *NODE, and ending when the 4 column fscanf is broken (by *END).
%
% INPUTS:   NodeName ('nodes.dyn')
%
% OUPUTS:   mpn (array of nodeID, x, y, z coords)
%
% Mark Palmeri
% mlp6@duke.edu
%
% Ned Danieley
*/

#include <stdio.h>
#include <stdlib.h>
#include "field.h"

#define LINE 160			/* space for input line */

struct nodeEntry *
readMpn(char *NodeName, int *numNodes)
{
int i;
FILE *nodesDyn;
char *buf;
size_t lineLength = LINE;
int numChars;
struct nodeEntry *nodes;

/* open input file */

    if ((nodesDyn = fopen(NodeName, "r")) == NULL) {
		fprintf(stderr, "couldn't open input file %s\n", NodeName);
		exit(EXIT_FAILURE);
		}

	if ((buf = (char *) malloc(lineLength + 1)) == NULL) {
		fprintf(stderr, "couldn't allocate space for line\n");
		exit(EXIT_FAILURE);
		}

	*numNodes = 0;
/* 	fprintf(stderr, "numNodes %d\n", *numNodes); */

/*
 * going to make two passes through the data because I need the number of
 * nodes to allocate space. might try using realloc instead once it's
 * working.
 */
	while ((numChars = getline(&buf, &lineLength, nodesDyn)) != -1) {
		if (buf[0] == '$') continue;
		if (buf[0] == '*') continue;

		(*numNodes)++;
		}
/* allocate space for nodes */

/* 	fprintf(stderr, "numNodes %d\n", *numNodes); */
	if ((nodes = (struct nodeEntry *)malloc(*numNodes * sizeof(struct nodeEntry))) == NULL) {
		fprintf(stderr, "couldn't allocate space for nodes\n");
		exit(EXIT_FAILURE);
		}

/* have to rewind input file before reading data */

	if (fseek(nodesDyn, 0, SEEK_SET) != 0) {
		fprintf(stderr, "couldn't seek input file\n");
		exit(EXIT_FAILURE);
		}

	i = 0;

	while ((numChars = getline(&buf, &lineLength, nodesDyn)) != -1) {
		if (buf[0] == '$') continue;
		if (buf[0] == '*') continue;
/* 		fprintf(stderr, "%s\n", buf); */
		sscanf(buf, "%d,%f,%f,%f", &nodes[i].nodeID, &nodes[i].x, &nodes[i].y, &nodes[i].z);
/* 		fprintf(stderr, "%d %f %f %f\n", nodes[i].nodeID, nodes[i].x, nodes[i].y, nodes[i].z); */
		i++;
		}

	fclose(nodesDyn);

	free(buf);

	return(nodes);
}
