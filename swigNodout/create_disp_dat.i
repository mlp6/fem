/* create_disp_dat.i */
%module create_disp_dat


%{
/* Put header files here or function declarations like below */
extern int create_disp_dat(char *inFileName, char *outFileName, int debug,
	int legacyNodes);
extern int correctE(char *disp);
extern int countNodeIDs(FILE *inFilePtr, int *nodes);
extern int writeNodeIDs(FILE *ptr, int num);
%}

extern int create_disp_dat(char *inFileName, char *outFileName, int debug,
	int legacyNodes);
extern int correctE(char *disp);
extern int countNodeIDs(FILE *inFilePtr, int *nodes);
extern int writeNodeIDs(FILE *ptr, int num);
