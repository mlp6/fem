/*
  Copyright (C) 2002
  by Livermore Software Technology Corp. (LSTC)
  All rights reserved
*/
#define __BUILD_LSDAF2C__
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#if !defined WIN32 && !defined MPPWIN
#include <dirent.h>
#include <unistd.h>
#define DIR_SEP '/'
#else
#include <windows.h>
#include <direct.h>
#define DIR_SEP '\\'
#define _errno win_errno
#endif
#include "lsda.h"
#include "lsda_internal.h"

#define Offset LSDA_Offset
#define Length LSDA_Length

#ifdef UNSCORE
#  define LSDA_REOPEN_C lsda_reopen_c_
#  define LSDA_FOPEN_C lsda_fopen_c_
#  define LSDA_OPEN_C lsda_open_c_
#  define LSDACLOSE lsdaclose_
#  define LSDA_FSIZE_C lsda_fsize_c_
#  define LSDAFILENUM lsdafilenum_
#  define LSDANEXTFILE lsdanextfile_
#  define LSDA_CD_C lsda_cd_c_
#  define LSDAFLUSH lsdaflush_
#  define LSDA_WRITE_C lsda_write_c_
#  define LSDA_READ_C lsda_read_c_
#  define LSDANEXTOPEN lsdanextopen_
#  define LSDASETRLEVEL lsdasetrlevel_
#  define LSDA_GETNAME_C lsda_getname_c_
#  define LSDA_GETBASENAME_C lsda_getbasename_c_
#  define LSDA_GETHANDLE_C lsda_gethandle_c_
#  define LSDA_QUERYVAR_C lsda_queryvar_c_
#  define LSDA_OPENDIR_C lsda_opendir_c_
#  define LSDACLOSEDIR lsdaclosedir_
#  define LSDA_READDIR_C lsda_readdir_c_
#else
#  ifdef PCWIN
#    define LSDA_GETBASENAME_C __stdcall LSDA_GETBASENAME_C
#    define LSDA_REOPEN_C __stdcall  LSDA_REOPEN_C
#    define LSDA_FOPEN_C __stdcall  LSDA_FOPEN_C
#    define LSDA_OPEN_C __stdcall  LSDA_OPEN_C
#    define LSDACLOSE __stdcall  LSDACLOSE
#    define LSDA_FSIZE_C __stdcall  LSDA_FSIZE_C
#    define LSDAFILENUM __stdcall  LSDAFILENUM
#    define LSDANEXTFILE __stdcall  LSDANEXTFILE
#    define LSDA_CD_C __stdcall  LSDA_CD_C
#    define LSDAFLUSH __stdcall  LSDAFLUSH
#    define LSDA_WRITE_C __stdcall  LSDA_WRITE_C
#    define LSDA_READ_C __stdcall  LSDA_READ_C
#    define LSDANEXTOPEN __stdcall  LSDANEXTOPEN
#    define LSDASETRLEVEL __stdcall  LSDASETRLEVEL
#    define LSDA_GETNAME_C __stdcall  LSDA_GETNAME_C
#    define LSDA_GETBASENAME_C __stdcall  LSDA_GETBASENAME_C
#    define LSDA_GETHANDLE_C __stdcall  LSDA_GETHANDLE_C
#    define LSDA_QUERYVAR_C __stdcall LSDA_QUERYVAR_C
#    define LSDA_OPENDIR_C __stdcall LSDA_OPENDIR_C
#    define LSDACLOSEDIR __stdcall LSDACLOSEDIR
#    define LSDA_READDIR_C __stdcall LSDA_READDIR_C
#  else
#    ifndef UPCASE
#      define LSDA_REOPEN_C lsda_reopen_c
#      define LSDA_FOPEN_C lsda_fopen_c
#      define LSDA_OPEN_C lsda_open_c
#      define LSDACLOSE lsdaclose
#      define LSDA_FSIZE_C lsda_fsize_c
#      define LSDAFILENUM lsdafilenum
#      define LSDANEXTFILE lsdanextfile
#      define LSDA_CD_C lsda_cd_c
#      define LSDAFLUSH lsdaflush
#      define LSDA_WRITE_C lsda_write_c
#      define LSDA_READ_C lsda_read_c
#      define LSDANEXTOPEN lsdanextopen
#      define LSDASETRLEVEL lsdasetrlevel
#      define LSDA_GETNAME_C lsda_getname_c
#      define LSDA_GETBASENAME_C lsda_getbasename_c
#      define LSDA_GETHANDLE_C lsda_gethandle_c
#      define LSDA_QUERYVAR_C lsda_queryvar_c
#      define LSDA_OPENDIR_C lsda_opendir_c
#      define LSDACLOSEDIR lsdaclosedir
#      define LSDA_READDIR_C lsda_readdir_c
#    endif
#  endif
#endif

typedef struct _ldc {
  int used;
  LSDADir *dir;
} DPTR;
static DPTR *mine = NULL;
static int mine_size = 0;

FortranInteger LSDA_REOPEN_C(
  char *filen,
  FortranInteger *filenum,
  Offset *offset,
  FortranInteger *ierr)
{
  FortranInteger retval =
     (FortranInteger) lsda_reopen(filen,(int) *filenum,(Offset) *offset);
  if(retval == -1)
    *ierr = (FortranInteger)lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
  return retval;
}
FortranInteger LSDA_FOPEN_C(
  char *filen,
  FortranInteger *filenum,
  Offset *offset,
  FortranInteger *handle,
  FortranInteger *ierr)
{
  FortranInteger retval =
     (FortranInteger) lsda_fopen(filen,(int) *filenum,(Offset) *offset,
                                 (int) *handle);
  if(retval == -1)
    *ierr = (FortranInteger)lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
  return retval;
}
FortranInteger LSDA_OPEN_C(
  char *filen,
  FortranInteger *mode,
  FortranInteger *ierr)
{
  FortranInteger retval = (FortranInteger) lsda_open(filen,(int) *mode);
  if(retval == -1)
    *ierr = (FortranInteger)lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
  return retval;
}
void LSDACLOSE(FortranInteger *handle, FortranInteger *ierr)
{
  int rc = lsda_close((int) *handle);
  if(rc == -1)
    *ierr = (FortranInteger) lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
}
Length LSDA_FSIZE_C(FortranInteger *handle, FortranInteger *ierr)
{
  Length retval = lsda_fsize((int) *handle);
  *ierr = (FortranInteger) lsda_errno;
  return retval;
}
FortranInteger LSDAFILENUM(FortranInteger *handle, FortranInteger *ierr)
{
  FortranInteger retval =  (FortranInteger) lsda_filenum((int) *handle);
  if(retval == -1)
    *ierr = (FortranInteger) lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
  return retval;
}
void LSDANEXTFILE(FortranInteger *handle, FortranInteger *ierr)
{
  int retval = lsda_nextfile((int) *handle);
  if(retval == -1)
    *ierr = (FortranInteger) lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
}
void LSDA_CD_C(FortranInteger *handle,char *path, FortranInteger *ierr)
{
  int retval = lsda_cd((int) *handle,path);
  if(retval == -1)
    *ierr = (FortranInteger) lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
}
void LSDAFLUSH(FortranInteger *handle, FortranInteger *ierr)
{
  int retval = lsda_flush((int) *handle);
  if(retval == -1)
    *ierr = (FortranInteger) lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
}
void LSDA_WRITE_C(FortranInteger *handle,FortranInteger *type_id,
                  char *name, FortranInteger *length, void *data,
                  FortranInteger *ierr)
{
  int retval = lsda_write((int) *handle,(int) *type_id,name,
                          (Length) *length, data);
  if(retval == -1)
    *ierr = (FortranInteger) lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
}
void LSDA_READ_C(FortranInteger *handle,FortranInteger *type_id,
                 char *name, FortranInteger *offset, FortranInteger *number,
                 void *data, FortranInteger *ierr)
{
  int retval = lsda_read((int) *handle,(int) *type_id,name,(int) *offset,
                         (int) *number, data);
  if(retval == -1)
    *ierr = (FortranInteger) lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
}
FortranInteger LSDANEXTOPEN(FortranInteger *handle, FortranInteger *ierr)
{
  FortranInteger retval = (FortranInteger) lsda_nextopen((int) *handle);
  if(retval == -1)
    *ierr = (FortranInteger) lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
  return retval;
}
void LSDASETRLEVEL(FortranInteger *level)
{
  lsda_setreportlevel((int) *level);
}
void LSDA_GETNAME_C(FortranInteger *handle,char *name,FortranInteger *len,
  FortranInteger *ierr)
{
  char *cp = lsda_getname((int) *handle);
  *len = strlen(cp);
  strcpy(name,cp);
  *ierr = LSDA_SUCCESS;
}
void LSDA_GETBASENAME_C(FortranInteger *handle,char *name,FortranInteger *len,
  FortranInteger *ierr)
{
  char *cp = lsda_getbasename((int) *handle);
  *len = strlen(cp);
  strcpy(name,cp);
  *ierr = LSDA_SUCCESS;
}
FortranInteger LSDA_GETHANDLE_C(
  char *filen,
  FortranInteger *ierr)
{
  FortranInteger retval = (FortranInteger) lsda_gethandle(filen);
  if(retval == -1)
    *ierr = (FortranInteger)lsda_errno;
  else
    *ierr = LSDA_SUCCESS;
  return retval;
}
void LSDA_QUERYVAR_C(
  FortranInteger *handle,
  char *name,
  FortranInteger *type,
  FortranInteger *len,
  FortranInteger *filenum,
  FortranInteger *ierr)
{
  int ltype, lfnum;
  Length llen;
  lsda_queryvar((int) *handle, name,&ltype,&llen,&lfnum);
  *type     = (FortranInteger) ltype;
  *len      = (FortranInteger) llen;
  *filenum  = (FortranInteger) lfnum;
  *ierr = LSDA_SUCCESS;
}
LSDA_OPENDIR_C(FortranInteger *handle, char *name, FortranInteger *ierr)
{
int i;

for(i=0; i<mine_size; i++)
  if(mine[i].used == 0) break;

if(i == mine_size) {
  mine = realloc(mine,(mine_size+10)*sizeof(DPTR));
  for(; i<mine_size+10; i++)
    mine[i].used = 0;
  i=mine_size;
  mine_size += 10;
}
mine[i].dir = lsda_opendir(*handle,name);
if(mine[i].dir == NULL) {
  *ierr = (FortranInteger) lsda_errno;
  return 0;
} else {  
  mine[i].used = 1;
  *ierr = LSDA_SUCCESS;
  return i+1;
}
}
void LSDACLOSEDIR(FortranInteger *index, FortranInteger *ierr)
{
int i = *index-1;

if(i >=0 && i < mine_size && mine[i].used) {
  lsda_closedir(mine[i].dir);
  mine[i].used = 0;
}
*ierr = LSDA_SUCCESS;
}
void LSDA_READDIR_C(
 FortranInteger *dir,
 char *name,
 FortranInteger *namelen,
 FortranInteger *typeid,
 FortranInteger *len,
 FortranInteger *filenum,
 FortranInteger *ierr)
{
  int index = *dir-1;
  if(index >= 0 && index < mine_size && mine[index].used) {
    int ltype, lfnum;
    Length llen;
    lsda_readdir(mine[index].dir,name,&ltype,&llen,&lfnum);
    *namelen = strlen(name);
    *typeid = (FortranInteger) ltype;
    *len = (FortranInteger) llen;
    *filenum = (FortranInteger) lfnum;
  } else {
    *namelen = 0;
    *typeid = -1;
    *len = -1;
    *filenum = -1;
  }
  *ierr = LSDA_SUCCESS;
}
  
void free_all_fdirs()
{
  if(mine_size > 0 && mine != NULL) free(mine);
}
