/* create_disp_dat_fast.i */
%module create_disp_dat_fast


%{
/* Put header files here or function declarations like below */
extern int create_disp_dat_fast(char *inFileName, char *outFileName, int debug,
	int legacyNodes);
extern int correctE(char *disp);
extern int countNodeIDs(FILE *inFilePtr, int *nodes);
extern int writeNodeIDs(FILE *ptr, int num);
%}

extern int create_disp_dat_fast(char *inFileName, char *outFileName, int debug,
	int legacyNodes);
extern int correctE(char *disp);
extern int countNodeIDs(FILE *inFilePtr, int *nodes);
extern int writeNodeIDs(FILE *ptr, int num);
