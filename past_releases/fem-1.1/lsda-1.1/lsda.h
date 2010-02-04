#ifndef LSDA_H
#define LSDA_H

#ifdef __cplusplus
extern "C"{
#endif

#undef EXTERN
#ifdef __BUILD_LSDA__
#define EXTERN
#else
#define EXTERN extern
#endif

typedef unsigned long	LSDA_Offset;
typedef unsigned long	LSDA_Length;
typedef unsigned char	LSDA_Command;
typedef unsigned char	LSDA_TypeID;

typedef struct _dbdir {
  void * btree;
  void *daf;
  int cont;
} LSDADir;

EXTERN int lsda_test(char *filen);
EXTERN int lsda_open_many(char **filen,int num);
EXTERN int lsda_open(char *filen,int mode);
EXTERN int lsda_write(int handle, int type_id,char *name,LSDA_Length length,void *data);
EXTERN int lsda_cd(int handle,char *path);
EXTERN LSDA_Length lsda_fsize(int handle);
EXTERN int lsda_nextfile(int handle);
EXTERN int lsda_close(int handle);
EXTERN int lsda_flush(int handle);
EXTERN int lsda_read(int handle, int type_id,char *name,int offset,int number,void *data);
EXTERN LSDADir *lsda_opendir(int handle, char *path);
EXTERN char *lsda_getpwd(int handle);
EXTERN void lsda_queryvar(int handle,char *name,int *type_id,LSDA_Length *length,
                int *filenum);
EXTERN void lsda_readdir(LSDADir *dir,char *name,int *type_id,LSDA_Length *length,
                int *filenum);
EXTERN LSDA_Length lsda_totalmemory(int handle);
EXTERN void lsda_closedir(LSDADir *dir);
EXTERN int lsda_util_countdir(int fhandle, char * dirname, int *ndir);
EXTERN int lsda_util_id2size(int type_id);
EXTERN char *lsda_getname(int handle);
EXTERN char *lsda_getbasename(int handle);
EXTERN int lsda_gethandle(char *name);
EXTERN int lsda_util_db2sg(int type_id);
EXTERN void free_all_lsda(void);
#ifndef __BUILD_LSDAF2C__
extern void free_all_fdirs();
#endif

#ifdef WIN32
#include <windows.h>
#ifndef MAXPATH
#define MAXPATH 2048
#endif
struct dirent {
  char d_name[MAXPATH];
};

typedef struct {
  WIN32_FIND_DATA wfd;
  HANDLE hfind,hfind0;
  struct dirent de;
  char dn_ptr[MAXPATH], filter[MAXPATH];
} DIR;
#undef MAXPATH
EXTERN DIR *opendir(char *spec,char *filter);
EXTERN struct dirent *readdir(DIR *pdir);
EXTERN void rewinddir(DIR *pdir);
EXTERN void closedir(DIR *pdir);
EXTERN int truncate(char *fname, size_t length);

#endif

#define	LSDA_READONLY		0
#define	LSDA_WRITEONLY		1
#define LSDA_SUCCESS 0

EXTERN int * _lsda_errno();
#define lsda_errno (* _lsda_errno())

/*
  Defined constants for the available data types
*/

#define LSDA_I1       1
#define LSDA_I2       2
#define LSDA_I4       3
#define LSDA_I8       4
#define LSDA_U1       5
#define LSDA_U2       6
#define LSDA_U4       7
#define LSDA_U8       8
#define LSDA_R4       9
#define LSDA_R8      10
#define LSDA_INT     11
#define LSDA_SHORT   12
#define LSDA_LONG    13
#define LSDA_UINT    14
#define LSDA_USHORT  15
#define LSDA_ULONG   16
#define LSDA_FLOAT   17
#define LSDA_DOUBLE  18
#define LSDA_INTEGER 19
#define LSDA_REAL    20
#define LSDA_DP      21

#ifdef __cplusplus
}
#endif

#endif
