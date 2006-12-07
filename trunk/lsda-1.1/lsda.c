/*
  Copyright (C) 2002
  by Livermore Software Technology Corp. (LSTC)
  All rights reserved

NOTE: things to consider working on/fixing some day.  In the open/openmany
routines, I'm not sure what will happen if the file name passed in has
a %XXX on the end already.  In the many case, should also watch for duplicate
names, or overlapping sets (ie, "file file%002 file" should collapse to just
"file").  Probably shouldn't try to expand "file%002" into a list, as it
would either give "file%002%XXX" or maybe "file%003".  But should 002 imply 003?
All I'm sure about at the moment is that things should work correctly if you
pass in a series of distinct base file names, and you want to open EVERYTHING
*/
#define __BUILD_LSDA__
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <ctype.h>
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
#define Command LSDA_Command
#define TypeID LSDA_TypeID

#ifdef VISIBLE
#define STATIC
#else
#define STATIC static
#endif

static char *fullfilename(LSDAFile *daf);
STATIC char *finddirmatch(char *name,DIR *dp);
STATIC int write_initialize(LSDAFile *daf);
STATIC int read_initialize(LSDAFile *daf);
STATIC int closeout_var(LSDAFile *daf);
STATIC int lsda_writesymboltable(LSDAFile *daf);
STATIC int lsda_writesymbol(char *ppath,char *curpath,
                           LSDATable *symbol,LSDAFile *daf);
STATIC LSDATable *lsda_readsymbol(LSDAFile *daf);
STATIC int lsda_readsymboltable(LSDAFile *daf);
STATIC void lsda_createbasictypes(LSDAFile *daf);
STATIC void CreateTypeAlias(LSDAFile *daf, char *alias, char *oldtype);
STATIC Length ReadLength(LSDAFile *daf);
STATIC Offset ReadOffset(LSDAFile *daf);
STATIC Command ReadCommand(LSDAFile *daf);
STATIC TypeID ReadTypeID(LSDAFile *daf);
STATIC void *ReadTrans(LSDAFile *daf,int FileLength,_CF Convert);
STATIC char *findpath(char *from, char *to);
STATIC int lsda_writecd(int handle,char *path);
_CF GetConversionFunction(IFile *ifile,LSDAType *typein, LSDAType *typeout);
STATIC void PruneSymbols(LSDAFile *daf,LSDATable *symbol);
static LSDA_Length SymbolSizes(LSDAFile *daf,LSDATable *symbol);
static int alloc_more_daf(int count);
static int lsda_open2(char *filen,int mode,int handle_in);

static int num_daf = 0;
static LSDAFile *da_store=NULL;
static int _errno = ERR_NONE;
static int report_level = 0;
static char _scbuf[1024];
int lsda_fopen(char *filen,int filenum, Offset offset,int want);

static int little_i = 1;
#define little_endian (*(char *)(&little_i))

#if defined WIN32 || defined MPPWIN
/*
  Start off with a few UNIX functions Win32 doesn't have....
*/

DIR *opendir(char *spec,char *filter)
{
/*
  opendir now not only search for the filter matches, but also search for 
  "*" wild card, which suppose to match every body.(if i cant find the matched filter)
*/
  DIR *pdir;
  char myfilter[MAX_PATH];
  char *ptr;

  pdir = (DIR *)malloc(sizeof(DIR));
  memset(pdir, 0, sizeof(DIR));
  _chdir(spec);
  strcpy(myfilter, filter);
  ptr = strrchr(myfilter, "*");  
  if(!ptr) strcat(myfilter, "*");
  pdir->hfind0 = pdir->hfind = FindFirstFile(myfilter, &pdir->wfd);
  if(pdir->hfind0!=(void*)0xFFFFFFFF){
    strcpy(pdir->filter, myfilter);
    strcpy(pdir->dn_ptr, spec);
  }
  else {
    pdir->hfind0 = pdir->hfind = FindFirstFile("*", &pdir->wfd);
    if(pdir->hfind0!=(void*)0xFFFFFFFF) {
      strcpy(pdir->dn_ptr, spec);
      strcpy(pdir->filter, "*");
    }
    else {
      free(pdir);
      return NULL;
    }
  }
  return pdir;
}

void rewinddir(DIR *pdir)
{
  FindClose(pdir->hfind0);
  pdir->hfind0 = pdir->hfind = FindFirstFile(pdir->filter, &pdir->wfd);
}

struct dirent *readdir(DIR *pdir)
{
    if (pdir->hfind) {
      strcpy(pdir->de.d_name, pdir->wfd.cFileName);
      if (!FindNextFile(pdir->hfind, &pdir->wfd))
        pdir->hfind = NULL;
      return &pdir->de;
    }
    return NULL;
}
void closedir(DIR *pdir)
{
    FindClose(pdir->hfind0);  
    free(pdir);
}

int truncate(char *fname, size_t length)
{
  char *tmpfile;
  char buf[1024];
  FILE *fout, *fin;
  int rdsize=0, cursize = 0;
  int breach =0;

  tmpfile = tempnam(NULL, "LSDA");  
  fout = fopen(tmpfile, "wb");
  fin = fopen(fname, "rb");
  if(fout ==NULL || fin == NULL) return -1;
  while(feof(fin)==0)
  {
    rdsize = 1024;
    if(cursize>(int)length)
    {
      rdsize = cursize - length +1024;
      breach = 1;
    }
    rdsize = fread(buf, sizeof(char), rdsize, fin);
    fwrite(buf, sizeof(char), rdsize, fout);
    if(breach) break;
    cursize+=1024;
  }
  fclose(fout);
  fclose(fin);
  rdsize = 1024;
  fout = fopen(fname,"wb");
  fin = fopen(tmpfile,"rb");
  if(fout == NULL || fin == NULL ) return -1;
  while(feof(fin)==0)
  {
    rdsize = fread(buf, sizeof(char), rdsize, fin);
    fwrite(buf, sizeof(char), rdsize, fout);
  }
  fclose(fin);
  fclose(fout);
  return 0;
}
#endif

static IFile *newIFile()
{
  IFile *ret = (IFile *)malloc(sizeof(IFile));
  memset(ret,0,sizeof(IFile));
  return ret;
}

int *_lsda_errno() { return &_errno; }

int lsda_reopen(char *filen,int filenum, Offset offset)
{
  int i = -1;
  return lsda_fopen(filen,filenum,offset,i);
}

int lsda_fopen(char *filen,int filenum, Offset offset,int want)
{
  DIR *dp;
  int i,j,len,handle;
  int file_compat;
  LSDAFile *daf;
  char *name;
  unsigned char header[16];
  char cur_pos[32],basename[64], *cp;
  int lastnum;
  char tname[8];
  Command cmd;
  LSDAType *type1,*type2;

  _errno = ERR_NONE;  /* reset error */
/*
  If the user specified a particular handle, get it if it is available
  else take next available handle.
*/
  if(want < 0) {
    for(i=0; i<num_daf; i++) {
      if(da_store[i].free) break;
    }
    if(i==num_daf && alloc_more_daf(10) < 0) return -1;
  } else {
    if(want >= num_daf) {
      if(alloc_more_daf(want+10-num_daf) < 0) return -1;
    } else {
      if(da_store[want].free == 0) return -1;
    }
    i = want;
  }
  if(filenum == 0 && offset == 0)
    return lsda_open2(filen,LSDA_WRITEONLY,i);  /* create for writing */
  handle = i;
  daf = da_store + i;
  InitLSDAFile(daf);
  lsda_createbasictypes(daf);
  daf->num_list = 1;
  daf->ifile = (IFile **) malloc(sizeof(IFile *));
  daf->ifile[0] = daf->curfile = newIFile();
  len = strlen(filen);
  if(filen[len-1] == DIR_SEP) filen[--len]=0;
  for(j=len-1; j>0; j--)
     if(filen[j] == DIR_SEP) {
       daf->curfile->dirname = (char *) malloc(j+1);
       memcpy(daf->curfile->dirname,filen,j);
       daf->curfile->dirname[j]=(char)0;
       daf->curfile->filename = (char *) malloc(len-j+8);
       strcpy(daf->curfile->filename,filen+j+1);
       break;
     }
  if(j == 0) {
    daf->curfile->dirname = (char *) malloc(2);
    strcpy(daf->curfile->dirname,".");
    daf->curfile->filename = (char *) malloc(len+1+8);
    strcpy(daf->curfile->filename,filen);
  }
  if(filenum > 0) {
    char ext[8],k;
    sprintf(ext,"%%%3.3d",filenum);
    strcat(daf->curfile->filename,ext);
  }
  daf->openmode=LSDA_WRITEONLY;
  /*
    Make sure the indicated file exists....
  */
  daf->fp = fopen(fullfilename(daf),"r+b");
  file_compat = 0;
  if(daf->fp == NULL) {   /* indicated file does not exist */
    file_compat=1;
  } else {
    fread(header,1,7,daf->fp);
    if(header[1] != sizeof(Length) ||
       header[2] != sizeof(Offset) ||
       header[3] != sizeof(Command) ||
       header[4] != sizeof(TypeID) ||
       header[5] != little_endian ||
       header[6] != FP_FORMAT) file_compat=2; /* exists, but may be different size/endianness */
  }
  if(file_compat==1){
   _errno = ERR_NOFILE;
   if(report_level > 0) fprintf(stderr,"lsda_reopen: file does not exist\n");
   goto cleanup;
  }
  if(filenum >= 0) {
/*
  Check to make sure offset given is a valid end of symbol table location
*/
    if(fseek(daf->fp,offset-header[2]-header[3],SEEK_SET) != 0){
     _errno = ERR_FSEEK;
     if(report_level > 0) fprintf(stderr,"lsda_reopen: fseek failed\n");
     goto cleanup;
    }
    /* To properly read the "command" field is a bit of a pain.  First, find the
     * proper conversion function, then feed it to the ReadTrans routine, along
     * with the in file size of the field */
    sprintf(tname,"I*%d",header[3]);
    type1 = daf->FindType(daf,tname);
    sprintf(tname,"I*%d",(int) sizeof(Command));
    type2 = daf->FindType(daf,tname);
    daf->curfile->bigendian = header[5];
    daf->curfile->ConvertCommand = GetConversionFunction(daf->curfile,type1,type2);
    cmd = *(Command *) ReadTrans(daf,header[3],GetConversionFunction(daf->curfile,type1,type2));
    if(_errno != ERR_NONE) {
      _errno = ERR_READ;
      if(report_level > 0)
        fprintf(stderr,"lsda_reopen: fread failed to read 1 byte\n");
      goto cleanup;
    }
    if(cmd != LSDA_ENDSYMBOLTABLE) {
     _errno = ERR_NOENDSYMBOLTABLE;
     if(report_level > 0)
       fprintf(stderr,"lsda_reopen: end of symbol table not found\n");
     goto cleanup;
    }
/*
  Set the "next symbol table" offset to 0
*/
    daf->stoffset = offset - header[2];
    daf->ateof = 0;   /* force fseek */
    if(fseek(daf->fp,daf->stoffset,SEEK_SET) != 0){
     _errno = ERR_FSEEK;
     if(report_level > 0) fprintf(stderr,"lsda_reopen: fseek to %ld failed\n",
                          (long) daf->stoffset);
     goto cleanup;
    }
    /* have to write at the correct number of words -- fortunately since we
     * are writing 0 there is no endianness problem... */
    memset(cur_pos,0,32);
    if(fwrite(cur_pos,header[2],1,daf->fp) != 1){
     _errno = ERR_WRITE;
     if(report_level > 0) fprintf(stderr,"lsda_reopen: fwrite failed\n");
     goto cleanup;
    }
/*
  Truncate file.  Could use ftruncate, but I can't find how to convert
  fp into a file descriptor.  Besides which ftruncate is unix only,
  and I'm hoping truncate might be more portable....
*/
    fclose(daf->fp);
    truncate(fullfilename(daf),offset);
    daf->fp = fopen(fullfilename(daf),"r+b");
  }
/*
  remove all files in this series with numbers > filenum
*/
  lastnum = -1;
  strcpy(basename,daf->curfile->filename);
  for(i=0,j=strlen(basename)-1; j>0; j--)
    if(isdigit(basename[j]))
      i=j;
    else
      break;
  if(i && j && basename[j] == '%') basename[j]=0;
#if defined WIN32 || defined MPPWIN
  dp = opendir(daf->curfile->dirname,basename);
#else
  dp = opendir(daf->curfile->dirname);
#endif
  if(!dp){
   _errno = ERR_OPENDIR;
   if(report_level > 0)
     fprintf(stderr,"lsda_reopen: error opening directory %s\n",daf->curfile->dirname);
   goto cleanup;
  }
  while(name = finddirmatch(basename,dp)) {
    len=strlen(name);
    for(i=0,j=strlen(name)-1; j>0; j--)
      if(isdigit(name[j]))
        i=j;
      else
        break;
    if(name[j] != '%') continue;
    if(i > 0) {
      j = atoi(name+i);
      if(j > lastnum) lastnum = j;
      if(j > filenum && filenum >= 0) {
        sprintf(_scbuf,"%s%c%s%%%3.3d",daf->curfile->dirname,DIR_SEP,basename,j);
        remove(_scbuf);
      }
    }
  }
  if(filenum < 0) {
    sprintf(daf->curfile->filename,"%s%%%3.3d",basename,lastnum);
    daf->continued = 0;
    daf->stmodified = 0;
    daf->fp = NULL;
    lsda_nextfile(handle);
  } else if(file_compat==2){
    /* Want to force future writing to a new file, since this one is
     * not fully compatible with me
     */
    daf->continued = 0;
    daf->stmodified = 0;
    lsda_nextfile(handle);
  }
/*
  these two lines together tell the system that, when it goes to
  write the next variable, we need a "CD" record first, and that
  it must use a complete path to the current directory (we don't know
  what the previous directory was...)

  Since we just opened the file, the CWD = "/", but even that should be
  written into the file on the first real write.
*/
  daf->lastpath[0]=0;
  daf->pathchanged=1;
  return handle;

cleanup:
 if(!daf) return -1;
 if(daf->fp) {
    fclose(daf->fp);
    daf->fp = NULL;
 }
 daf->FreeTable(daf,daf->top);
 daf->FreeTypes(daf);
 daf->free = 1;
 return -1;
}

int lsda_open_many(char **filen,int num)
{
int i,j,k,len,handle;
LSDAFile *daf;
/*
  Get next available handle
*/
_errno = ERR_NONE;  /* reset error */

for(i=0; i<num_daf; i++) {
  if(da_store[i].free) break;
}
if(i==num_daf && alloc_more_daf(10) < 0) return -1;
handle = i;
daf = da_store + i;
InitLSDAFile(daf);
daf->num_list = num;
/* If we are worried about the user passing in duplicate file names,
 * could go through the list here and wipe out any that are dups */
daf->ifile = (IFile **) malloc(num*sizeof(IFile *));
for(k=0; k<num; k++) {
  len = strlen(filen[k]);
  daf->ifile[k] = daf->curfile = newIFile();
  if(filen[k][len-1] == DIR_SEP) filen[k][--len]=0;
  for(j=len-1; j>0; j--)
     if(filen[k][j] == DIR_SEP) {
       daf->curfile->dirname = (char *) malloc(j+1);
       memcpy(daf->curfile->dirname,filen[k],j);
       daf->curfile->dirname[j]=(char)0;
       daf->curfile->filename = (char *) malloc(len-j+8);
       strcpy(daf->curfile->filename,filen[k]+j+1);
       break;
     }
  if(j == 0) {
    daf->curfile->dirname = (char *) malloc(2);
    strcpy(daf->curfile->dirname,".");
    daf->curfile->filename = (char *) malloc(len+1+8);
    strcpy(daf->curfile->filename,filen[k]);
  }
}
daf->openmode=LSDA_READONLY;
/*
  Open and initialize the file(s)
*/
if(read_initialize(daf) >= 0) return handle;
/*
  Some kind of error occured -- free what we allocated and
  get out.
*/
if(daf->ifile) {
  for(i=0; i<num; i++) {
    if(daf->ifile[k]) {
      if(daf->ifile[k]->dirname) free(daf->ifile[k]->dirname);
      if(daf->ifile[k]->filename) free(daf->ifile[k]->filename);
      free(daf->ifile[k]);
    }
  }
  free(daf->ifile);
  daf->ifile = NULL;
}
daf->free = 1;
return -1;
}
STATIC int lsda_checkforsymboltable(LSDAFile *daf)
{
  Command cmd;
  Offset table_pos, end_pos;
  Length stlen;
/*
  Check to see if this looks like a symbol table....
*/
  table_pos = ReadOffset(daf);
  if(table_pos == 0) return 0;   /* end of file -- no more symbol tables */
  if(_errno != ERR_NONE) return -1;
  if(fseek(daf->fp,table_pos,SEEK_SET) < 0) return -1;
  stlen = ReadLength(daf);
  if(_errno != ERR_NONE) return -1;
  cmd = ReadCommand(daf);
  if(_errno != ERR_NONE) return -1;
  if(cmd != LSDA_BEGINSYMBOLTABLE) return -1;
  end_pos = stlen+table_pos -
            (daf->curfile->FileLengthSize +
             daf->curfile->FileCommandSize +
             daf->curfile->FileOffsetSize);
  if(fseek(daf->fp,end_pos,SEEK_SET) < 0) return -1;
  /* see if end of symbol table is where it should be */
  stlen = ReadLength(daf);
  if(_errno != ERR_NONE) return -1;
  cmd = ReadCommand(daf);
  if(_errno != ERR_NONE) return -1;
  if(cmd != LSDA_ENDSYMBOLTABLE) return -1;
  /* Leave offset word for next call */
  return 1;
}
int lsda_test(char *filen)
{
  /* check to see if this might be a legit LSDA file */
  unsigned char header[8];
  char tname[8];
  Command cmd;
  LSDAType *type1,*type2;
  int first = 1,len;
  int i,j,retval;
  LSDAFile daf0, *daf;

  daf = &daf0;
  InitLSDAFile(daf);
  len = strlen(filen);
  daf->curfile = newIFile();
  if(filen[len-1] == DIR_SEP) filen[--len]=0;
  daf->curfile->dirname=(char *)malloc(len+10);
  daf->curfile->filename=(char *)malloc(len+10);
  for(j=len-1; j>0; j--)
    if(filen[j] == DIR_SEP) {
      strcpy(daf->curfile->dirname,filen);
      daf->curfile->dirname[j]=0;
      strcpy(daf->curfile->filename,filen+j+1);
      break;
    }
  if(j == 0) {
    strcpy(daf->curfile->dirname,".");
    strcpy(daf->curfile->filename,filen);
  }
  daf->openmode=LSDA_READONLY;

/*
  Try opening and reading this file.
*/
  if((daf->fp = fopen(filen,"rb")) == NULL) return 0;  /* failed */
  if(fread(header,1,7,daf->fp) < 7) { /* fail */
    fclose(daf->fp);
    goto done0;
  }
  daf->curfile->FileLengthSize = header[1];
  daf->curfile->FileOffsetSize = header[2];
  daf->curfile->FileCommandSize= header[3];
  daf->curfile->FileTypeIDSize = header[4];
  daf->curfile->bigendian      = header[5];
  daf->curfile->fp_format      = header[6];
  if(daf->curfile->FileLengthSize  < 1 || daf->curfile->FileLengthSize  > 8 ||
     daf->curfile->FileOffsetSize  < 1 || daf->curfile->FileOffsetSize  > 8 ||
     daf->curfile->FileCommandSize < 1 || daf->curfile->FileCommandSize > 8 ||
     daf->curfile->FileTypeIDSize  < 1 || daf->curfile->FileTypeIDSize  > 8 ||
     daf->curfile->bigendian < 0 || daf->curfile->bigendian > 1) {
    fclose(daf->fp);
    goto done0;
  }
  lsda_createbasictypes(daf);
/*
  Set conversion functions for length, offset, etc
*/
  sprintf(tname,"I*%d",daf->curfile->FileLengthSize);
  type1 = daf->FindType(daf,tname);
  sprintf(tname,"I*%d",(int) sizeof(Length));
  type2 = daf->FindType(daf,tname);
  daf->curfile->ConvertLength = GetConversionFunction(daf->curfile,type1,type2);

  sprintf(tname,"I*%d",daf->curfile->FileOffsetSize);
  type1 = daf->FindType(daf,tname);
  sprintf(tname,"I*%d",(int) sizeof(Offset));
  type2 = daf->FindType(daf,tname);
  daf->curfile->ConvertOffset = GetConversionFunction(daf->curfile,type1,type2);

  sprintf(tname,"I*%d",daf->curfile->FileCommandSize);
  type1 = daf->FindType(daf,tname);
  sprintf(tname,"I*%d",(int) sizeof(Command));
  type2 = daf->FindType(daf,tname);
  daf->curfile->ConvertCommand = GetConversionFunction(daf->curfile,type1,type2);

  sprintf(tname,"I*%d",daf->curfile->FileTypeIDSize);
  type1 = daf->FindType(daf,tname);
  sprintf(tname,"I*%d",(int) sizeof(TypeID));
  type2 = daf->FindType(daf,tname);
  daf->curfile->ConvertTypeID = GetConversionFunction(daf->curfile,type1,type2);
/*
  OK, now check for what look like reasonable symbol table(s).
*/
  fseek(daf->fp,header[0],SEEK_SET);
  ReadLength(daf);
  cmd = ReadCommand(daf);
  if(_errno == ERR_READ || cmd != LSDA_SYMBOLTABLEOFFSET) {  /* error */
    _errno = ERR_NONE;  /* reset read error */
    retval=0;
    goto done1;
  }
  daf->stoffset=ftell(daf->fp);
  for(i=0; i<5; i++) {
    j = lsda_checkforsymboltable(daf);
    if(j == -1) break;    /* bad file */
    if(j == 0) i=5;       /* end of file  -- count as OK */
  }
  retval = i < 5 ? 0 : 1;
done1:
  fclose(daf->fp);
  daf->FreeTypes(daf);
done0:
  free(daf->curfile->dirname);
  free(daf->curfile->filename);
  free(daf->curfile);
  return retval;
}
int lsda_open(char *filen,int mode)
{
  return lsda_open2(filen,mode,-1);
}
static int lsda_open2(char *filen,int mode,int handle_in)
{
  int i,j,len,handle;
  LSDAFile *daf;
  char *cp;
  DIR *dp;

  _errno = ERR_NONE;  /* reset error */
/*
  Get next available handle
*/
  if(handle_in < 0) {
    for(i=0; i<num_daf; i++) {
      if(da_store[i].free) break;
    }
    if(i==num_daf && alloc_more_daf(10) < 0) return -1;
    handle = i;
  } else {
    handle = handle_in;  /* guaranteed to be ok.... */
  }
  daf = da_store + i;
  InitLSDAFile(daf);
  daf->num_list = 1;
  daf->ifile = (IFile **) malloc(sizeof(IFile *));
  daf->ifile[0] = daf->curfile = newIFile();

  len = strlen(filen);
  if(filen[len-1] == DIR_SEP) filen[--len]=0;
  for(j=len-1; j>0; j--)
     if(filen[j] == DIR_SEP) {
       daf->curfile->dirname = (char *) malloc(j+1);
       memcpy(daf->curfile->dirname,filen,j);
       daf->curfile->dirname[j]=(char)0;
       daf->curfile->filename = (char *) malloc(len-j+8);
       strcpy(daf->curfile->filename,filen+j+1);
       break;
     }
  if(j == 0) {
    daf->curfile->dirname = (char *) malloc(2);
    strcpy(daf->curfile->dirname,".");
    daf->curfile->filename = (char *) malloc(len+1+8);
    strcpy(daf->curfile->filename,filen);
  }
  daf->openmode=mode;
  /*
    Open and initialize the file
  */
  switch(mode) {
     case LSDA_READONLY:  /* open existing file and preserve data */
       if(read_initialize(daf) < 0) goto cleanup;
       return handle;
     case LSDA_WRITEONLY:  /* create file */
#if defined WIN32 || defined MPPWIN
       if((dp = opendir(daf->curfile->dirname,daf->curfile->filename)) == NULL) {
#else
       if((dp = opendir(daf->curfile->dirname)) == NULL) {
#endif
         _errno = ERR_OPENDIR;
         if(report_level > 0) fprintf(stderr,
      "lsda_open: Cannot open directory %s\nCheck permissions\n",daf->curfile->dirname);
         goto cleanup;
       }
       while(cp=finddirmatch(daf->curfile->filename,dp)) {
         remove(cp);
       }
       closedir(dp);
       if((daf->fp = fopen(filen,"w+b"))==NULL) {
         _errno = ERR_OPENFILE;
         if(report_level > 0) fprintf(stderr,
      "lsda_open: Cannot open file %s\nCheck permissions\n",filen);
         goto cleanup;
       }
       if(write_initialize(daf)<0) goto cleanup;
       return handle;
    }
cleanup:
  if(daf->ifile) {
    if(daf->curfile) {
      if(daf->curfile->dirname) free(daf->curfile->dirname);
      if(daf->curfile->filename) free(daf->curfile->filename);
      free(daf->curfile);
    }
    free(daf->ifile);
    daf->ifile = NULL;
  }
  daf->free = 1;
  return -1;
}

static int alloc_more_daf(int count)
{
  int i;
  if(da_store)
    da_store = (LSDAFile *) realloc(da_store,(num_daf+count)*sizeof(LSDAFile));
  else
    da_store = (LSDAFile *) malloc(count*sizeof(LSDAFile));
  if(!da_store){
    _errno = ERR_MALLOC;
    if(report_level > 0)
      fprintf(stderr,"alloc_more_daf: malloc of %d failed\n",count);
    return -1;
  }
  for(i=num_daf ; i<num_daf+count; i++)
    da_store[i].free = 1;
  num_daf += count;
  return 1;
}

STATIC int write_initialize(LSDAFile *daf)
{
unsigned char header[16];
int handle = daf-da_store;
Length rlen;
Command cmd;
Offset offset;

header[0] = 8;               /* number of bytes in header, this included */
header[1] = sizeof(Length);  /* size of int used in data record lengths */
header[2] = sizeof(Offset);  /* size of int used in data file offsets */
header[3] = sizeof(Command); /* size of int used in data file commands */
header[4] = sizeof(TypeID);  /* size of int used in data file typeids */
header[5] = little_endian;   /* 0 for bigendian, 1 for little_endian */
header[6] = FP_FORMAT;       /* 0 = IEEE */
header[7] = 0;

fseek(daf->fp,0,SEEK_SET);
if(fwrite(header,1,8,daf->fp) < 8) goto write_error;
/*
  Create empty space for symbol table pointer
*/
rlen = sizeof(Length)+sizeof(Command)+sizeof(Offset);
cmd = LSDA_SYMBOLTABLEOFFSET;
if(fwrite(&rlen,sizeof(Length),1,daf->fp) < 1) goto write_error;
if(fwrite(&cmd,sizeof(Command),1,daf->fp) < 1) goto write_error;
offset = 0;
daf->stoffset = ftell(daf->fp);
if(fwrite(&offset,sizeof(Offset),1,daf->fp) < 1) goto write_error;
if(lsda_cd(handle,"/") < 0) { fclose(daf->fp); daf->fp=NULL; return -1; }
if(lsda_writecd(handle,"/") < 0) { fclose(daf->fp); daf->fp=NULL; return -1; }
strcpy(daf->lastpath,"/");
lsda_createbasictypes(daf);
return 1;

write_error:
 _errno = ERR_WRITE;
 if(report_level > 0) {
   fprintf(stderr,
  "write_initialize: Write error on file %s\n",fullfilename(daf));
 }
 if(daf->fp) fclose(daf->fp);
 daf->fp=NULL;
 return -1;
}

STATIC void lsda_createbasictypes(LSDAFile *daf)
{
LSDAType *type;
char tname[32];
/*
  Create the necessary intrinsic types
*/
 if(daf->ntypes > 0) return;  /* have already been in here... */
 type = daf->CreateType(daf,"I*1");
  type->length_on_disk = type->length = 1;
 type = daf->CreateType(daf,"I*2");
  type->length_on_disk = type->length = 2;
 type = daf->CreateType(daf,"I*4");
  type->length_on_disk = type->length = 4;
 type = daf->CreateType(daf,"I*8");
  type->length_on_disk = type->length = 8;
 type = daf->CreateType(daf,"U*1");
  type->length_on_disk = type->length = 1;
 type = daf->CreateType(daf,"U*2");
  type->length_on_disk = type->length = 2;
 type = daf->CreateType(daf,"U*4");
  type->length_on_disk = type->length = 4;
 type = daf->CreateType(daf,"U*8");
  type->length_on_disk = type->length = 8;
 type = daf->CreateType(daf,"R*4");
  type->length_on_disk = type->length = 4;
 type = daf->CreateType(daf,"R*8");
  type->length_on_disk = type->length = 8;
/*
  And type aliases
*/
  sprintf(tname,"I*%d",(int) sizeof(int));
  CreateTypeAlias(daf,"int",tname);

  sprintf(tname,"I*%d",(int) sizeof(short));
  CreateTypeAlias(daf,"short",tname);

  sprintf(tname,"I*%d",(int) sizeof(long));
  CreateTypeAlias(daf,"long",tname);

  sprintf(tname,"U*%d",(int) sizeof(unsigned int));
  CreateTypeAlias(daf,"uint",tname);

  sprintf(tname,"U*%d",(int) sizeof(unsigned short));
  CreateTypeAlias(daf,"ushort",tname);

  sprintf(tname,"U*%d",(int) sizeof(unsigned long));
  CreateTypeAlias(daf,"ulong",tname);

  sprintf(tname,"R*%d",(int) sizeof(float));
  CreateTypeAlias(daf,"float",tname);

  sprintf(tname,"R*%d",(int) sizeof(double));
  CreateTypeAlias(daf,"double",tname);

  sprintf(tname,"I*%d",(int) sizeof(FortranInteger));
  CreateTypeAlias(daf,"integer",tname);

  sprintf(tname,"R*%d",(int) sizeof(FortranReal));
  CreateTypeAlias(daf,"real",tname);

  sprintf(tname,"R*%d",(int) sizeof(FortranDouble));
  CreateTypeAlias(daf,"double precision",tname);
}
STATIC void CreateTypeAlias(LSDAFile *daf, char *alias, char *oldtype)
{
LSDAType *otype, *ntype;

  ntype = daf->CreateType(daf,alias);
  otype = daf->FindType(daf,oldtype);
  ntype->alias = otype;
}
STATIC int read_initialize(LSDAFile *daf)
{
/*
  Read in the existing symbol table (or reconstruct it as needed....someday)
*/
unsigned char header[8];
char tname[8];
Command cmd;
LSDAType *type1,*type2;
char *name,fullname[1024];
IFile *ifile;
int namelen;
int retval= -1;
int i,j,is_newfile;
DIR *dp;
int org_num_list = daf->num_list;

for(i=0; i==0 || i<org_num_list; i++) {
  daf->curfile = daf->ifile[i];
  namelen = strlen(daf->ifile[i]->filename);

#if defined WIN32 || defined MPPWIN
  dp = opendir(daf->ifile[i]->dirname,daf->ifile[i]->filename);
#else
  dp = opendir(daf->ifile[i]->dirname);
#endif

  if(dp == NULL) {
    _errno = ERR_OPENDIR;
    if(report_level > 0) fprintf(stderr,
    "read_initialize: Cannot open directory %s\nCheck permissions\n",
    daf->ifile[i]->dirname);
    return -1;
  }
/*
  Try opening and reading all files of the form filename[%digits]
  where the [%digits] are optional.  As far as I can see, I
  don't really care what order we open them in....
*/
  while(name = finddirmatch(daf->ifile[i]->filename,dp)) {
    if(strlen(name) == namelen) {  /* opened base file */
      ifile = daf->ifile[i];
      is_newfile = 0;
    } else {
      ifile = newIFile();
      ifile->dirname = (char *) malloc(strlen(daf->ifile[i]->dirname)+1);
      ifile->filename = (char *) malloc(strlen(name)+1);
      strcpy(ifile->dirname,daf->ifile[i]->dirname);
      strcpy(ifile->filename,name);
      is_newfile = 1;
    }
    sprintf(fullname,"%s%c%s",ifile->dirname,DIR_SEP,ifile->filename);
    if((daf->fp = fopen(fullname,"rb")) == NULL) { /* skip this file */
      free(ifile->dirname);
      free(ifile->filename);
      free(ifile);
      if(!is_newfile) daf->ifile[i] = NULL;
      continue;
    }
    if(fread(header,1,7,daf->fp) < 7) { /* skip this file */
      fclose(daf->fp);
      free(ifile->dirname);
      free(ifile->filename);
      free(ifile);
      if(!is_newfile) daf->ifile[i] = NULL;
      daf->fp=NULL;
      continue;
    }

    ifile->FileLengthSize = header[1];
    ifile->FileOffsetSize = header[2];
    ifile->FileCommandSize= header[3];
    ifile->FileTypeIDSize = header[4];
    ifile->bigendian      = header[5];
    ifile->fp_format      = header[6];
    lsda_createbasictypes(daf);
/*
  Set conversion functions for length, offset, etc
*/
    sprintf(tname,"I*%d",ifile->FileLengthSize);
    type1 = daf->FindType(daf,tname);
    sprintf(tname,"I*%d",(int) sizeof(Length));
    type2 = daf->FindType(daf,tname);
    ifile->ConvertLength = GetConversionFunction(ifile,type1,type2);

    sprintf(tname,"I*%d",ifile->FileOffsetSize);
    type1 = daf->FindType(daf,tname);
    sprintf(tname,"I*%d",(int) sizeof(Offset));
    type2 = daf->FindType(daf,tname);
    ifile->ConvertOffset = GetConversionFunction(ifile,type1,type2);

    sprintf(tname,"I*%d",ifile->FileCommandSize);
    type1 = daf->FindType(daf,tname);
    sprintf(tname,"I*%d",(int) sizeof(Command));
    type2 = daf->FindType(daf,tname);
    ifile->ConvertCommand = GetConversionFunction(ifile,type1,type2);

    sprintf(tname,"I*%d",ifile->FileTypeIDSize);
    type1 = daf->FindType(daf,tname);
    sprintf(tname,"I*%d",(int) sizeof(TypeID));
    type2 = daf->FindType(daf,tname);
    ifile->ConvertTypeID = GetConversionFunction(ifile,type1,type2);

/*
  Read in symbol table
  Should put reconstruction code in here eventually...
*/
    fseek(daf->fp,header[0],SEEK_SET);
    daf->curfile = ifile;  /* so ReadTrans routines will work */
    ReadLength(daf);
    cmd = ReadCommand(daf);
    if(_errno == ERR_READ || cmd != LSDA_SYMBOLTABLEOFFSET) {  /* skip this file for now */
      _errno = ERR_NONE;  /* reset read error */
      if(report_level > 0) {
        fprintf(stderr,"Error reading symbol table in file %s\n",name);
        fprintf(stderr,"  Skipping this file\n");
      }
      free(ifile->dirname);
      free(ifile->filename);
      free(ifile);
      if(!is_newfile) daf->ifile[i] = NULL;
      fclose(daf->fp);
      daf->fp=NULL;
      continue;
    }
    daf->stoffset=ftell(daf->fp);
    if(lsda_readsymboltable(daf) == 1) { /* OK, keep this one */
      if(is_newfile) {
        daf->ifile = (IFile **) realloc(daf->ifile,(daf->num_list+1)*sizeof(IFile *));
        daf->ifile[daf->num_list++] = ifile;
      }
      retval=1;
    } else {
      free(ifile->dirname);
      free(ifile->filename);
      free(ifile);
      if(!is_newfile) daf->ifile[i] = NULL;
    }
    fclose(daf->fp);
    daf->fp=NULL;
  }
  closedir(dp);
}
daf->curfile = NULL;
daf->fp = NULL;
daf->stmodified = 0;
daf->cwd = daf->top;
/*
 * In case we had problems opening one or more of the files, reduce the ifile
 * list here
 */
for(i=j=0; i<daf->num_list; i++) {
  if(daf->ifile[i] != NULL)
    daf->ifile[j++] = daf->ifile[i];
}
daf->num_list = j;
return retval;
}

STATIC int closeout_var(LSDAFile *daf)
{
  Length len = ftell(daf->fp) - daf->var->offset;

  if(fseek(daf->fp,daf->var->offset,SEEK_SET) < 0) {
    _errno = ERR_FSEEK;
    if(report_level > 0) {
      fprintf(stderr,"closeout_var: seek error on file %s\n",
              fullfilename(daf));
    }
    return -1;
  }
  if(fwrite(&len,sizeof(Length),1,daf->fp) < 1) {
    _errno = ERR_WRITE;
    if(report_level > 0) {
      fprintf(stderr,"closeout_var: write error on file %s\n",
              fullfilename(daf));
    }
    return -1;
  }
  daf->ateof = 0;
  daf->continued = 0;
  daf->var->length = (len-sizeof(Length)-sizeof(Command)-sizeof(TypeID)-
     strlen(daf->var->name)-1)/LSDASizeOf(daf->var->type);
  return 1;
}

int lsda_write(int handle, int type_id,char *name,Length length,void *data)
{
  LSDAFile *daf = da_store + handle;
  int tsize;
  TypeID tid;
  Length rlen;
  Command cmd = LSDA_DATA;
  char nlen;
  LSDATable *var;
  LSDAType *type;
  char prevpath[MAXPATH],cwd[MAXPATH];
  int j,retval;
  char lname[256],ldir[256];

  if(name[0]==0) {  /* continue writing previous variable */
    if(!daf->var)  {
      _errno = ERR_NOCONT;
      if(report_level > 0)
        fprintf(stderr,"Empty variable name used while not currently writing a variable\n");
      return -1;
    }
    daf->continued = 1;
    tsize = LSDASizeOf(daf->var->type);
    retval = fwrite(data,tsize,length,daf->fp);
    if(retval < length) _errno = ERR_WRITE;
    return retval;
  }
  cwd[0]=0;
/*
  Writing new variable.  If were not finished with the old one,
  close it out.
*/
  if(daf->continued) {
    if(closeout_var(daf) < 0) return -1;
  }
  if(!daf->ateof) {
    fseek(daf->fp,0,SEEK_END);
    daf->ateof = 1;
  }
/*
  Check for directory portion in variable name
*/
  nlen = strlen(name);
  for(j=nlen-1; j>0; j--)
     if(name[j] == '/') {
       strcpy(ldir,name);
       ldir[j]=(char)0;
       strcpy(lname,name+j+1);
       break;
     }
  if(j == 0) {
    strcpy(lname,name);
  } else {
    strcpy(cwd,daf->GetCWD(daf));
    lsda_cd(handle,ldir);
  }
/*
  Update CWD in file if necessary
*/
  if(daf->pathchanged) {
    strcpy(prevpath,daf->lastpath);
    strcpy(daf->lastpath,daf->GetCWD(daf));
    if(lsda_writecd(handle,findpath(prevpath,daf->lastpath)) < 0) {
      if(report_level > 0) fprintf(stderr,"lsda_write: updating CWD\n");
      if(cwd[0])lsda_cd(handle,cwd);
      return -1;
    }
  }
  if((type=daf->FindTypeByID(daf,type_id)) == NULL) {
    _errno = ERR_DATATYPE;
    if(report_level > 0) fprintf(stderr,
        "lsda_write: unrecognized data type %d\n",type_id);
    if(cwd[0])lsda_cd(handle,cwd);
    return -1;
  }
  var=daf->CreateVar(daf,type,lname);
  var->offset = (Offset) ftell(daf->fp);
  var->length = (Length) length;
  var->ifile = daf->curfile;
  var->dirty = 1;
  daf->stmodified = 1;
  nlen = (char) strlen(var->name);

  daf->var=var;

  tsize = LSDASizeOf(type);
  tid = LSDAId(type);
  rlen = sizeof(Length)+sizeof(Command)+sizeof(TypeID)+nlen+1+length*tsize;
  if(fwrite(&rlen,sizeof(Length),1,daf->fp) < 1) goto write_error;
  if(fwrite(&cmd,sizeof(Command),1,daf->fp) < 1) goto write_error;
  if(fwrite(&tid,sizeof(TypeID),1,daf->fp) < 1) goto write_error;
/*
  The variable name is stored as a 1 char length and then a non-terminated
  string
*/
  if(fwrite(&nlen,1,1,daf->fp) < 1) goto write_error;
  if(fwrite(lname,1,(int)nlen,daf->fp) < nlen) goto write_error;
  retval = fwrite(data,tsize,length,daf->fp);
  if(retval < length) _errno = ERR_WRITE;
  if(cwd[0])lsda_cd(handle,cwd);
  return retval;

write_error:
   _errno = ERR_WRITE;
   if(report_level > 0) {
     fprintf(stderr,
        "lsda_write: write error on file %s\n",fullfilename(daf));
   }
   if(cwd[0])lsda_cd(handle,cwd);
   return -1;
}

int lsda_cd(int handle,char *path)
{
  LSDAFile *daf = da_store + handle;
  int flag = 1;
  if(daf->openmode == LSDA_READONLY) flag = 0;
  if(daf->ChangeDir(daf,path,flag) == NULL) {
    _errno = ERR_CD;
    if(report_level > 0) {
      fprintf(stderr,
    "lsda_cd: Cannot cd to %s in file %s.  Most likely a component of\nthe path is not a directory\n",
      path,daf->curfile->filename);
    }
    return -1;
  }
  daf->pathchanged=1;
  return 1;
}
STATIC int lsda_writecd(int handle,char *path)
{
  LSDAFile *daf = da_store + handle;
  Length rlen;
  int len;
  Command cmd = LSDA_CD;

  if(path == NULL) {
    daf->pathchanged=0;
    return 1;
  }
/*
  If were not finished with the previous variable close it out.
*/
  if(daf->continued) {
    if(closeout_var(daf) < 0) {
      if(report_level > 0)
        fprintf(stderr,"lsda_writecd: error closing out variable\n");
      return -1;
    }
  }
  if(!daf->ateof) {
    fseek(daf->fp,0,SEEK_END);
    daf->ateof = 1;
  }
  len = strlen(path);
  rlen = sizeof(Length)+sizeof(Command)+len;

  if(fwrite(&rlen,sizeof(Length),1,daf->fp) < 1) goto write_error;
  if(fwrite(&cmd,sizeof(Command),1,daf->fp) < 1) goto write_error;
  if(fwrite(path,1,len,daf->fp) < len) goto write_error;
  daf->pathchanged=0;
  return 1;

write_error:
  _errno = ERR_WRITE;
  if(report_level > 0) {
    fprintf(stderr,
      "lsda_writecd: write error on file %s\n",fullfilename(daf));
  }
  return -1;
}

Length lsda_fsize(int handle)
{
  LSDAFile *daf = da_store+handle;

  if(!daf->fp) return 0;  /* no file currently opened */
  if(!daf->ateof) {
    fseek(daf->fp,0,SEEK_END);
    daf->ateof = 1;
  }
  return((Length) ftell(daf->fp));  /* should add estimate of Symbol Table size too? */
}
int lsda_filenum(int handle)
{
  LSDAFile *daf = da_store+handle;
  int i,ret;
  char *cp;
  cp = strrchr(daf->curfile->filename,'%');  /* find % */
  if(!cp) return 0;
  ret = atoi(cp+1);                          /* convert following to number */
  for(cp++; *cp; cp++)
    if(!isdigit(*cp)) ret=0;                 /* but only if all following are digits */
  return(ret);
}

int lsda_nextfile(int handle)
{
  LSDAFile *daf = da_store+handle;
  int i,cur;
  char *cp;

  if(daf->openmode == LSDA_READONLY) return 0;
  if(daf->continued) {
    if(closeout_var(daf) < 0) goto cleanup;
  }
  if(daf->stmodified && lsda_writesymboltable(daf) < 0) goto cleanup;
  if(daf->fp) fclose(daf->fp);
  daf->fp=NULL;
  daf->cwd = daf->top;

  cp = strrchr(daf->curfile->filename,'%');  /* find % */
  if(!cp) {
    cur=0;
  } else {
    cur = atoi(cp+1);                          /* convert following to number */
    for(cp++; *cp; cp++)
      if(!isdigit(*cp)) cur=0;                 /* but only if all following are digits */
  }
  /* Build new file name.  Just overwrite the same ifile pointer since we
   * are done with it now.... */
  if(cur == 0) {
    strcat(daf->curfile->filename,"%001");
  } else {
    cp = strrchr(daf->curfile->filename,'%');
    sprintf(cp+1,"%3.3d",cur+1);
  }
  if((daf->fp = fopen(fullfilename(daf),"w+b"))!=NULL) {
    if(write_initialize(daf) < 0) goto cleanup;
  } else {
    _errno = ERR_OPENFILE;
    if(report_level > 0)
      fprintf(stderr,"lsda_nextfile: error opening file %s",fullfilename(daf));
    return -1;
  }
  return cur+1;

cleanup:
  if(report_level > 0) fprintf(stderr,"lsda_nextfile: error\n");
  return -1;
}

STATIC int SwitchFamilyMember(LSDAFile *daf,LSDATable *var)
{
  if(daf->fp) {
/*
  these would make sense if we were writing, but this routine
  is only ever called when reading.  Somday may have read/write
  access?  I suppose it wouldn't be hard, so long as they know
  the limitations....but we'd have to hold the whole symbol
  table in memory, so LSDA_WRITEONLY is still more efficient for
  DYNA purposes.

    if(daf->continued) closeout_var(daf);
    if(daf->stmodified) lsda_writesymboltable(daf);
*/
    fclose(daf->fp);
    daf->fp=NULL;
  }
  daf->curfile = var->ifile;
  if((daf->fp = fopen(fullfilename(daf),"r+b")) == NULL) {
    _errno = ERR_OPENFILE;
    if(report_level > 0)
      fprintf(stderr,"lsda_SwitchFamilyMember: error opening %s",fullfilename(daf));
    return -1;
  }
  daf->ateof = 0;
  daf->continued = 0;
  daf->stmodified = 0;
  return 1;
}

int lsda_close(int handle)
{
  LSDAFile *daf = da_store+handle;

  if(daf->continued && closeout_var(daf) < 0) goto cleanup;
  if(daf->stmodified && lsda_writesymboltable(daf) < 0) goto cleanup;
  if(daf->fp) fclose(daf->fp);
  daf->fp=NULL;
  daf->FreeTable(daf,daf->top);
  daf->FreeTypes(daf);
  if(daf->num_list) {
    int i;
    for(i=0; i<daf->num_list; i++) {
      free(daf->ifile[i]->dirname);
      free(daf->ifile[i]->filename);
      free(daf->ifile[i]);
    }
    free(daf->ifile);
  }
  daf->free = 1;
  return 1;

cleanup:
  if(report_level > 0) {
    fprintf(stderr,
      "lsda_close: error closing file %s\n",fullfilename(daf));
  }
  _errno = ERR_CLOSE;
  return -1;
}

int lsda_flush(int handle)
{
  LSDAFile *daf = da_store+handle;
  if(daf->continued) {
    if(closeout_var(daf) < 0) goto cleanup;
  }
  if(daf->stmodified && lsda_writesymboltable(daf) < 0) goto cleanup;
  fflush(daf->fp);
  return 1;
cleanup:
  if(report_level > 0) {
    fprintf(stderr,"lsda_flush: error\n");
  }
  return -1;
}
int lsda_read(int handle, int type_id,char *name,int offset,int number,void *data)
{
  LSDAFile *daf = da_store + handle;
  LSDAType *type = daf->FindTypeByID(daf,type_id);
  _CF Convert;
  int tsize;
  Offset foffset;
  int ret;
  char buf[BUFSIZE], *cp;
  LSDATable *var;
  int tsizedisk;
  int j,k,kk,perbuf;

  if(type == NULL) {
    _errno = ERR_DATATYPE;
    if(report_level > 0) {
      fprintf(stderr,"lsda_read: unrecognized data type %d",type_id);
      fprintf(stderr, " while reading file %s\n",daf->curfile ? daf->curfile->filename : NULL);
    }
    return -1;
  }
/*
  get var info from symbol table: size of each item, starting offset
*/
  var=daf->FindVar(daf,name);
  if(var == NULL) {
    _errno = ERR_NOVAR;
    if(report_level > 0)
      fprintf(stderr,
        "lsda_read: variable %s not found while reading file %s\n CWD=%s\n",
         name,daf->curfile ? daf->curfile->filename : NULL,daf->GetCWD(daf));
    return -1;
  }
  tsize = LSDASizeOf(type);
  tsizedisk = LSDASizeOf(var->type);
  Convert = GetConversionFunction(var->ifile,var->type,type);

  foffset = var->offset +var->ifile->FileLengthSize+
            var->ifile->FileCommandSize+var->ifile->FileTypeIDSize+
            strlen(var->name)+1+offset*tsizedisk;

  if((var->ifile != daf->curfile) && SwitchFamilyMember(daf,var) < 0) {
    if(report_level > 0) fprintf(stderr,"lsda_read: error\n");
    return -1;
  }

  fseek(daf->fp,foffset,SEEK_SET);
  cp=buf;
  if(Convert) {
  /*
    Read, in chunks, as many items as we can that will fit into
    our buffer, then convert them into the user's space
  */
    perbuf = BUFSIZE/tsizedisk;
    if(perbuf < 1) { /* Yoikes!  Big data item! */
      cp = (char *) malloc(tsizedisk);
      if(!cp) fprintf(stderr,"lsda_read: Malloc failed!\n"); exit(0);
      perbuf=1;
    }
    k=perbuf;
    ret=0;
    for(j=0; j<number; j+= perbuf) {
      if(j+k > number) k=number-j;
      kk = fread(cp,tsizedisk,k,daf->fp);
      Convert(cp,((char *)data)+j*tsize,kk);
      ret=ret+kk;
      if(kk < k) break;
    }
    if(cp != buf) free(cp);
  } else {
    ret=fread((char *) data,tsize,number,daf->fp);
  }
  if(ret < number) {
    _errno = ERR_READ;
    if(report_level > 0) {
      fprintf(stderr,
        "lsda_read: error reading file %s\n",fullfilename(daf));
    }
  }
  return ret;
}
STATIC int lsda_writesymboltable(LSDAFile *daf)
{
  Command cmd;
  Length rlen;
  Offset table_pos, cur_pos, offset_pos;
  char path1[MAXPATH],path2[MAXPATH];
/*
  If were not finished with the previous variable close it out.
*/
  if(daf->continued) {
    if(closeout_var(daf) < 0) goto cleanup1;
  }
  if(!daf->ateof) {
    fseek(daf->fp,0,SEEK_END);
    daf->ateof = 1;
  }
  table_pos = ftell(daf->fp);
  rlen = 0;
  if(fwrite(&rlen,sizeof(Length),1,daf->fp) < 1) goto cleanup;
  cmd = LSDA_BEGINSYMBOLTABLE;
  if(fwrite(&cmd,sizeof(Command),1,daf->fp) < 1) goto cleanup;

  path1[0] = path2[0] = 0;
  if(lsda_writesymbol(path1,path2,daf->top,daf) < 0) goto cleanup1;

/*
  Write end of symbol table record
*/
  rlen = sizeof(Length)+sizeof(Command)+sizeof(Offset);
  if(fwrite(&rlen,sizeof(Length),1,daf->fp) < 1) goto cleanup;
  cmd = LSDA_ENDSYMBOLTABLE;
  if(fwrite(&cmd,sizeof(Command),1,daf->fp) < 1) goto cleanup;
  offset_pos = ftell(daf->fp);
  cur_pos = 0;  /* offset to next piece of table -- 0=> no next piece */
  if(fwrite(&cur_pos,sizeof(Offset),1,daf->fp) < 1) goto cleanup;
/*
  Update length of this symbol table block
*/
  cur_pos = ftell(daf->fp);
  rlen = cur_pos-table_pos;
  fseek(daf->fp,table_pos,SEEK_SET);
  if(fwrite(&rlen,sizeof(Length),1,daf->fp) < 1) goto cleanup;
/*
  Update the file offset that points to this chunk of the symbol table
*/
  fseek(daf->fp,daf->stoffset,SEEK_SET);
  if(fwrite(&table_pos,sizeof(Offset),1,daf->fp) < 1) goto cleanup;
  daf->stoffset = offset_pos;
  daf->ateof = 0;
  daf->stmodified = 0;
/*
  If file is not being read, delete unneeded symbols
*/
  if(daf->openmode == LSDA_WRITEONLY) PruneSymbols(daf,daf->top);
  return 1;

cleanup1:
  if(report_level > 0) fprintf(stderr,"lsda_writesymboltable: error\n");
  return -1;

cleanup:
  _errno = ERR_WRITE;
  if(report_level > 0) {
    fprintf(stderr,
        "lsda_writesymboltable: write error on file %s\n",
        fullfilename(daf));
  }
  return -1;
}

STATIC void PruneSymbols(LSDAFile *daf,LSDATable *symbol)
{
  int i;
  LSDATable **kids;
  int numkids;

  if(symbol->type) {    /* a variable */
    if(!symbol->dirty) {
      daf->FreeTable(daf,symbol);
      return;
    }
  } else {
    if(symbol->children) {
      numkids = BT_numentries(symbol->children);
      if(numkids) {
        kids = (LSDATable **) BT_list(symbol->children);
        for(i=0; i<numkids; i++)
          PruneSymbols(daf,kids[i]);
        free(kids);
      }
    }
    if(!symbol->children || BT_numentries(symbol->children) == 0) {
      if(symbol != daf->top && symbol != daf->cwd)
        daf->FreeTable(daf,symbol);
    }
  }
}
LSDA_Length lsda_totalmemory(int handle)
{
  LSDAFile *daf = da_store + handle;
  if(!daf->top) return (LSDA_Length) 0;
  return SymbolSizes(daf,daf->top);
}

STATIC LSDA_Length SymbolSizes(LSDAFile *daf,LSDATable *symbol)
{
  int cont;
  LSDATable *child;
  LSDA_Length tot = 0;

  if(symbol->type) {    /* a variable */
    tot = symbol->length*LSDASizeOf(symbol->type);
  } else {
    if(symbol->children) {
      for(cont=0; ; ) {
       child = (LSDATable *) BT_enumerate(symbol->children,&cont);
       if(!child) break;
       tot += SymbolSizes(daf,child);
      }
    }
  }
  return tot;
}

STATIC int lsda_readsymboltable(LSDAFile *daf)
{
  Command cmd;
  Offset table_pos, offset_pos;
/*
  Read symbol table from file.
*/
  if(fseek(daf->fp,daf->stoffset,SEEK_SET) < 0) {
    _errno = ERR_FSEEK;
    goto cleanup;
  }
  table_pos = ReadOffset(daf);
  if(_errno != ERR_NONE) goto cleanup;

  while(table_pos) {
    if(fseek(daf->fp,table_pos,SEEK_SET) < 0) {
      _errno = ERR_FSEEK;
      goto cleanup;
    }
    ReadLength(daf);
    if(_errno != ERR_NONE) goto cleanup;

    cmd = ReadCommand(daf);
    if(_errno != ERR_NONE) goto cleanup;
    if(cmd != LSDA_BEGINSYMBOLTABLE) {
      _errno = ERR_NOBEGINSYMBOLTABLE;
      goto cleanup;
    }
    while(lsda_readsymbol(daf))
      ;
/*
  Check for end of symbol table record
*/
    ReadLength(daf);
    if(_errno != ERR_NONE) goto cleanup;
    cmd = ReadCommand(daf);
    if(_errno != ERR_NONE) goto cleanup;
    if(cmd != LSDA_ENDSYMBOLTABLE) {
      _errno = ERR_NOENDSYMBOLTABLE;
      goto cleanup;
    }
    offset_pos = ftell(daf->fp);
    table_pos = ReadOffset(daf);
    if(_errno != ERR_NONE) goto cleanup;
  }
  daf->stoffset = offset_pos;
  daf->ateof = 0;
  return 1;

cleanup:
  if(report_level > 0)
     fprintf(stderr,
      "lsda_readsymboltable: error %d on file %s at byte %ld\n",
      _errno,fullfilename(daf),(long) ftell(daf->fp));
  return -1;
}
STATIC int lsda_writesymbol(char *ppath,char *curpath,
                           LSDATable *symbol,LSDAFile *daf)
{
  Command cmd;
  Length rlen;
  int nlen;
  char *pp;
  int pplen;
  int i,keeplen,cont;
  int retval = 0;
  LSDATable *child;

  if(symbol->type && symbol->dirty) {  /* dirty variable */
    nlen = strlen(symbol->name);
    if(strcmp(ppath,curpath)) { /* have to write a directory entry */
      pp = findpath(ppath,curpath);
      pplen = strlen(pp);
      rlen = pplen+sizeof(Length)+sizeof(Command);
      if(fwrite(&rlen,sizeof(Length),1,daf->fp) < 1) goto cleanup;
      cmd = LSDA_CD;
      if(fwrite(&cmd,sizeof(Command),1,daf->fp) < 1) goto cleanup;
      if(fwrite(pp,1,pplen,daf->fp) < pplen) goto cleanup;
      strcpy(ppath,curpath);
    }
    rlen = sizeof(Length)+sizeof(Command)+sizeof(TypeID)+nlen+
           sizeof(Offset)+sizeof(Length);
    if(fwrite(&rlen,sizeof(Length),1,daf->fp) < 1) goto cleanup;
    cmd = LSDA_VARIABLE;
    if(fwrite(&cmd,sizeof(Command),1,daf->fp) < 1) goto cleanup;
    if(fwrite(symbol->name,1,nlen,daf->fp) < nlen) goto cleanup;
    if(fwrite(&symbol->type->id,sizeof(TypeID),1,daf->fp) < 1) goto cleanup;
    if(fwrite(&symbol->offset,sizeof(Offset),1,daf->fp) < 1) goto cleanup;
    if(fwrite(&symbol->length,sizeof(Length),1,daf->fp) < 1) goto cleanup;
    symbol->dirty = 0;
    retval = 1;
  } else if(!symbol->type && symbol->children) {   /* do subdir */
    keeplen = strlen(curpath);
    if(keeplen == 0)
      strcpy(curpath,"/");
    else if(keeplen == 1)
      sprintf(curpath+keeplen,"%s",symbol->name);
    else
      sprintf(curpath+keeplen,"/%s",symbol->name);
/*
  Go through two times:  First write any simple variables,
  then do subdirectories
*/
    for(cont=0; ;) {
      child = (LSDATable *) BT_enumerate(symbol->children,&cont);
      if(!child) break;
      if(child->type) {
        i=lsda_writesymbol(ppath,curpath,child,daf);
        if(i < 0) {
          if(report_level > 0) fprintf(stderr,"lsda_writesymbol: error\n");
          return -1;
        }
      }
    }
    for(cont=0; ;) {
      child = (LSDATable *) BT_enumerate(symbol->children,&cont);
      if(!child) break;
      if(!child->type) {
        i=lsda_writesymbol(ppath,curpath,child,daf);
        if(i < 0) {
          if(report_level > 0) fprintf(stderr,"lsda_writesymbol: error\n");
          return -1;
        }
      }
    }
    retval = 1;
    curpath[keeplen]=0;
  }
  return(retval);

cleanup:
  _errno = ERR_WRITE;
  if(report_level > 0) {
    fprintf(stderr,
      "lsda_writesymbol: write error on file %s",fullfilename(daf));
  }
  return -1;
}
STATIC LSDATable *lsda_readsymbol(LSDAFile *daf)
{
  Command cmd;
  Length rlen;
  int nlen;
  char name[256];
  TypeID type_id;
  LSDATable *symbol;
  LSDAType *type;
  
  rlen=ReadLength(daf);
  if(_errno == ERR_READ) goto cleanup;
  cmd=ReadCommand(daf);
  if(_errno == ERR_READ) goto cleanup;
  if(cmd == LSDA_VARIABLE) {
    nlen = rlen-
         2*daf->curfile->FileLengthSize-daf->curfile->FileCommandSize-
           daf->curfile->FileTypeIDSize-daf->curfile->FileOffsetSize;
    if(fread(name,1,nlen,daf->fp) < nlen) {
      _errno = ERR_READ;
      goto cleanup;
    }
    name[nlen] = 0;
    type_id = ReadTypeID(daf);
    if(_errno == ERR_READ) goto cleanup;
    type = daf->FindTypeByID(daf,type_id);
    if(type == NULL) {
      _errno = ERR_NOTYPEID;
      if(report_level > 0) {
        fprintf(stderr,
          "lsda_readsymbol: No corresponding id for %d in file %s\n",
          (int) type_id,fullfilename(daf));
      }
      return NULL;
    }
    symbol = daf->CreateVar(daf,type,name);
    symbol->offset = ReadOffset(daf);
    if(_errno == ERR_READ) goto cleanup;
    symbol->length = ReadLength(daf);
    if(_errno == ERR_READ) goto cleanup;
    symbol->ifile = daf->curfile;
  } else if(cmd == LSDA_CD) {
    nlen = rlen-daf->curfile->FileLengthSize-daf->curfile->FileCommandSize;
    if(fread(name,1,nlen,daf->fp) < nlen) {
      _errno = ERR_READ;
      goto cleanup;
    }
    name[nlen]=0;
    if(daf->ChangeDir(daf,name,1) == NULL) {
      _errno = ERR_CD;
      if(report_level > 0) {
        fprintf(stderr,"lsda_readsymbol: Cannot cd to %s in file %s\n",
                name,fullfilename(daf));
        fprintf(stderr,"Most likely a component of\nthe path is not a directory\n");
      }
      return NULL;
    }
    symbol = daf->cwd;
  } else {
    fseek(daf->fp,-daf->curfile->FileLengthSize-daf->curfile->FileCommandSize,SEEK_CUR);
    return NULL;
  }
  return symbol;

cleanup:
  if(report_level > 0) {
      fprintf(stderr,
      "lsda_readsymbol: read error on file %s",fullfilename(daf));
  }
  return NULL;
}
#ifdef DUMP_DEBUG
lsda_dumpst(int handle)
{
  LSDAFile *daf = da_store + handle;
  dumpit("/",daf->top);
}
dumpit(char *cwd, LSDATable *symbol)
{
  char dir[1024];
  int cont;
  LSDATable *child;

  if(symbol->type) {
    printf("Var %s%s, type = %s,  file %s, offset = %d, length = %d\n",cwd,
      symbol->name,symbol->type->name,symbol->ifile->filename, symbol->offset,symbol->length);
  } else {
    if(strcmp(cwd,"/")==0 && strcmp(symbol->name,"/") == 0) {
        strcpy(dir,"/");
    } else {
      sprintf(dir,"%s%s/",cwd,symbol->name);
    }
    printf("Dir %s\n",dir);
    if(symbol->children) {
      for(cont=0; ;) {
        child = (LSDATable *) BT_enumerate(symbol->children,&cont);
        if(!child) break;
        dumpit(dir,child);
      }
    }
  }
}
#endif

STATIC Length ReadLength(LSDAFile *daf)
{
  return * (Length *) ReadTrans(daf,daf->curfile->FileLengthSize,daf->curfile->ConvertLength);
}
STATIC Offset ReadOffset(LSDAFile *daf)
{
  return * (Offset *) ReadTrans(daf,daf->curfile->FileOffsetSize,daf->curfile->ConvertOffset);
}
STATIC Command ReadCommand(LSDAFile *daf)
{
  return * (Command *) ReadTrans(daf,daf->curfile->FileCommandSize,daf->curfile->ConvertCommand);
}
STATIC TypeID ReadTypeID(LSDAFile *daf)
{
  return * (TypeID *) ReadTrans(daf,daf->curfile->FileTypeIDSize,daf->curfile->ConvertTypeID);
}
STATIC void *ReadTrans(LSDAFile *daf,int FileLength,_CF Convert)
{
  static char buf[16],buf2[16];

  if(fread(buf,1,FileLength,daf->fp) < 1) {
    memset(buf,0,16);
    _errno = ERR_READ;
    if(report_level > 0) {
      fprintf(stderr,
          "ReadTrans: error reading %d bytes from file %s\n",
          FileLength,fullfilename(daf));
    }
    return (void *) buf;
  }
  if(Convert) {
    Convert(buf,buf2,1);
    return (void *) buf2;
  } else {
    return (void *) buf;
  }
}
STATIC char *findpath(char *from, char *to)
{
int i,j,k;
int lastdir;
int lento = strlen(to);
int lenrel;
static char relpath[256];


lastdir=0;
if(from[0]==0 ) return to;            /* we HAVE no previous path.... */
if(from[1]==0 ) return to;            /* "from" is root dir */
for(i=0; from[i] && from[i] == to[i]; i++)  /* find common part of path */
  if(from[i] == '/') lastdir=i;
if(from[i] == '/' && !to[i]) lastdir=i;

if(!from[i] && !to[i]) return NULL;   /* identical */


if(!from[i] && to[i] == '/') return to+i+1;  /* to is a subdir of from */

/*
  Count number of ".." we'd need to do a relative path
*/

for(j=lastdir,k=0; from[j]; j++)
  if(from[j] == '/') k++;

lenrel = 3*k + (lento-lastdir);

if(lenrel < lento) {
  for(i=0; i<3*k; i+=3) {
    relpath[i  ] = '.';
    relpath[i+1] = '.';
    relpath[i+2] = '/';
  }
  if(lento == lastdir)   /* to is a subdir of from */
    relpath[i-1]=0;      /* strip off last / */
  else
    sprintf(relpath+i,"%s",to+lastdir+1);
  return relpath;
} else
  return to;
}

STATIC char *finddirmatch(char *name,DIR *dp)
{
  struct dirent *file;
  int i,nlen;
  char *cp;

again:
  while(file = readdir(dp)) {
/*
  return this file if it is of the form "name%XXXX"
*/
    nlen = strlen(name);
    cp = file->d_name;
    for(i=0; i<nlen; i++,cp++)
      if(*cp != name[i]) goto again;
    if(*cp == 0) return name;
    if(*cp != '%') goto again;
    for(cp++; *cp; cp++)
       if(!isdigit(*cp)) goto again;
    return file->d_name;
  }
  return NULL;
}
LSDADir * lsda_opendir(int handle,char *path)
{
  LSDAFile *daf = da_store + handle;
  LSDATable *var;
  LSDADir *dir;
  var=daf->FindVar(daf,path);
  if(var == NULL || var->type) {
    _errno = ERR_OPNDIR;
    if(report_level > 0) 
      fprintf(stderr,
    "lsda_opendir: cannot find directory %s in file %s%c%s",path,
    daf->curfile->dirname,DIR_SEP,daf->curfile->filename);
    return NULL;
  }
  dir = (LSDADir *) malloc(sizeof(LSDADir));
  dir->btree = var->children;
  dir->cont = 0;
  dir->daf = (void *) daf;
  return dir;
}
void lsda_readdir(LSDADir *dir,char *name,int *type_id,Length *length,
                int *filenum)
{
  LSDATable *var;

  if(!dir || !dir->btree) { /* they forgot to call opendir, or dir is empty */
    name[0]=0;
    *type_id = -1;
    *length = *filenum = -1;
  }
  var = (LSDATable *) BT_enumerate(dir->btree,&dir->cont);
  if(var) {
    strcpy(name,var->name);
    if(var->type) {
      *type_id = LSDAId(var->type);
      *length = var->length;
      *filenum = 0;  /* obsolete */
    } else {
      *type_id = 0;
      if(var->children)
        *length = BT_numentries(var->children);
      else
        *length = 0;
      *filenum = -1;
    }
  } else {
    name[0]=0;
    *type_id = -1;
    *length = *filenum = -1;
  }
}
void lsda_queryvar(int handle,char *name,int *type_id,Length *length,
                int *filenum)
{
  LSDAFile *daf = da_store + handle;
  LSDATable *var;
  var=daf->FindVar(daf,name);
  if(var) {
    if(var->type) {
      *type_id = LSDAId(var->type);
      *length = var->length;
      *filenum = 0;  /* obsolete */
/*
      *offset = var->offset +daf->FileLengthSize+daf->FileCommandSize+
            daf->FileTypeIDSize + strlen(var->name)+1;
*/
    } else {
      *type_id= 0;
      if(var->children)
        *length = BT_numentries(var->children);
      else
        *length = 0;
      *filenum = -1;
    }
  } else {
    *type_id= -1;
    *length = *filenum = -1;
  }
}
void lsda_closedir(LSDADir *dir)
{
  free(dir);
}
char *lsda_getpwd(int handle)
{
  LSDAFile *daf = da_store + handle;
  return daf->GetCWD(daf);
}
void lsda_setreportlevel(int level)
{
  report_level = level;
}
int lsda_nextopen(int handle)
{
int i;

if(handle < 0) handle = -1;

for(i=handle+1; i<num_daf; i++)
   if(da_store[i].free == 0) return i;

return -1;
}
static char *fullfilename(LSDAFile *daf)
{
  sprintf(_scbuf,"%s%c%s",daf->curfile->dirname,DIR_SEP,daf->curfile->filename);
  return _scbuf;
}
void lsda_perror(char *string)
{
  fprintf(stderr,"%s : ",string);
  switch (_errno) {
    case ERR_NONE:              /* no error */
       fprintf(stderr,"No error\n");
       break;
    case ERR_MALLOC:            /* malloc failed */
       fprintf(stderr,"Malloc failed\n");
       break;
    case ERR_NOFILE:            /* non-existent file */
       fprintf(stderr,"Attempt to reopen non-existant file\n");
       break;
    case ERR_FSEEK:             /* fseek failed */
       fprintf(stderr,"Fseek failed\n");
       break;
    case ERR_READ:              /* read error on file */
       fprintf(stderr,"Read error\n");
       break;
    case ERR_WRITE:             /* write error on file */
       fprintf(stderr,"Write error\n");
       break;
    case ERR_NOENDSYMBOLTABLE:  /* append, but end of symbol table not found */
       fprintf(stderr,"Attempt to truncate file at invalid location\n");
       break;
    case ERR_OPENDIR:           /* error opening directory for file */
       fprintf(stderr,"Error opening directory for file operation\n");
       break;
    case ERR_OPENFILE:          /* error opening file */
       fprintf(stderr,"Error opening file\n");
       break;
    case ERR_NOCONT:            /* empty name to write when not continuing */
       fprintf(stderr,"Write with empty variable name when\n");
       fprintf(stderr,"last file operation was not a write\n");
       break;
    case ERR_DATATYPE:          /* write with unknown data type */
       fprintf(stderr,"Write attempt with unknown variable type\n");
       break;
    case ERR_NOTYPEID:          /* read unknown type id from file */
       fprintf(stderr,"Read unknown type id from file\n");
       break;
    case ERR_CD:                /* illegal cd attempt in file */
       fprintf(stderr,"Illegal directory change\n");
       fprintf(stderr,"Most likely a component in the specified path");
       fprintf(stderr,"already exists as a\n variable\n");
       break;
    case ERR_CLOSE:             /* error on close ?? */
       fprintf(stderr,"Error closing file\n");
       break;
    case ERR_NOVAR:             /* read on non-existant variable */
       fprintf(stderr,"Attempt to read on non-existant variable\n");
       break;
    case ERR_NOBEGINSYMBOLTABLE:/* missing Begin Symbol Table */
       fprintf(stderr,"Error: missing BEGINSYMBOLTABLE\n");
       break;
    case ERR_OPNDIR:            /* open directory in file for query */
       fprintf(stderr,"Error opening directory for query\n");
       break;
    default:
       fprintf(stderr,"Unknown error %d\n",_errno);
       break;
  }
  _errno = ERR_NONE;
}
char *lsda_getname(int handle)
{
  LSDAFile *daf = da_store + handle;
  char *cp, *c;
  if(!daf->curfile && daf->ifile) daf->curfile = daf->ifile[0];
  if(!daf->curfile) { _scbuf[0]=0; return _scbuf; }
  sprintf(_scbuf,"%s%c%s",daf->curfile->dirname,DIR_SEP,daf->curfile->filename);
  cp = strrchr(_scbuf,'%');  /* strip out the part after % */
  if(cp) {
    for(c=cp+1; *c; c++)
      if(!isdigit(*c)) cp=NULL;
  }
  if(cp) *cp=0;
  return _scbuf;
}

char *lsda_getbasename(int handle)
{
  LSDAFile *daf = da_store + handle;
  char *cp, *c;
  if(!daf->curfile && daf->ifile) daf->curfile = daf->ifile[0];
  if(!daf->curfile) { _scbuf[0]=0; return _scbuf; }
  strcpy(_scbuf,daf->curfile->filename);
  cp = strrchr(_scbuf,'%');  /* strip out the part after % */
  if(cp) {
    for(c=cp+1; *c; c++)
      if(!isdigit(*c)) cp=NULL;
  }
  if(cp) *cp=0;
  return _scbuf;
}

int lsda_gethandle(char *filen)
{
int i,len;
LSDAFile *daf;
/*
  Scan open handles and check for one matching the given name
*/
_errno = ERR_NONE;  /* reset error */
len = strlen(filen);

for(i=0; i<num_daf; i++) {
  if(!da_store[i].free) {
    daf = da_store+i;
    if(!daf->curfile && daf->ifile) daf->curfile = daf->ifile[0];
    if(!daf->curfile) continue;
    strcpy(_scbuf,daf->curfile->filename);
    if(_scbuf[len] == '%') _scbuf[len]=0;
    if(strcmp(_scbuf,filen)==0) return i;
  }
}
return -1;
}

int lsda_util_countdir(int fhandle, char * dirname, int *ndir)
{
  LSDADir *dir;
  char childdirname[80];
  int tid, fno;
  LSDA_Length len;

  if(lsda_cd(fhandle, dirname)<0) return -1;
  dir = lsda_opendir(fhandle, ".");
  if(dir==NULL) return -1;
  do {
    lsda_readdir(dir, childdirname, &tid, &len, &fno);
    if(childdirname[0]) (*ndir)++;
  } while(childdirname[0]);
  lsda_closedir(dir);
  return *ndir;
}

int lsda_util_id2size(int type_id)
{
  switch(type_id)
  {
  case LSDA_I1: return sizeof(char);
  case LSDA_SHORT:
  case LSDA_I2: return sizeof(short);
  case LSDA_INT:
  case LSDA_INTEGER:
  case LSDA_I4: return sizeof(int);
  case LSDA_LONG:
  case LSDA_I8: return sizeof(long);
  case LSDA_U1: return sizeof(unsigned char);
  case LSDA_USHORT:
  case LSDA_U2: return sizeof(unsigned short);
  case LSDA_UINT:
  case LSDA_U4: return sizeof(unsigned int);
  case LSDA_ULONG:
  case LSDA_U8: return sizeof(unsigned long);
  case LSDA_FLOAT:
  case LSDA_REAL:
  case LSDA_R4: return sizeof(float);
  case LSDA_DOUBLE:
  case LSDA_DP:
  case LSDA_R8: return sizeof(double);
  }
  return 0;
}

int lsda_util_db2sg(int type_id)
{
  switch(type_id)
  {
  case LSDA_DOUBLE: return LSDA_FLOAT;
  case LSDA_DP: return LSDA_REAL;
  case LSDA_R8: return LSDA_R4;
  case LSDA_U8: return LSDA_U4;
  case LSDA_ULONG: return LSDA_UINT;
  case LSDA_I8: return LSDA_I4;
  case LSDA_LONG: return LSDA_INT;  
  }
  return type_id;
}
void free_all_tables(void);
void free_all_types(void);
#ifndef NO_FORTRAN
void free_all_fdirs(void);
#endif
void free_all_lsda(void)
{
  int i;
/*
  First close all open files
*/
  for(i=0; i<num_daf; i++) {
    if(!da_store[i].free) lsda_close(i);
  }
/*
  Now free everything
*/
  free(da_store);
  free_all_tables();
  free_all_types();
#ifndef NO_FORTRAN
  free_all_fdirs();
#endif
}
