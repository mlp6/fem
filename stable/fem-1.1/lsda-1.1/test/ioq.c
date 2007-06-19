/*
  Copyright (C) 2002
  by Livermore Software Technology Corp. (LSTC)
  All rights reserved
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "lsda.h"

void printvar(int handle,char *namein);
void listdir(int handle);
void build_name(char *name,int typeid);

main(int argc, char *argv[])
{
int handle;
int typeid, filenum;
LSDA_Length length;
char cmd[256];

if(argc < 2) {
  printf("syntax: %s file\n",argv[0]);
  exit(1);
}
lsda_setreportlevel(1);
if(lsda_test(argv[1]) == 0) {
  printf("%s is not a valid LSDA file\n",argv[1]);
  exit(0);
}
handle = lsda_open_many(argv+1,argc-1);
length = lsda_totalmemory(handle);
printf("File contains %ld bytes of data\n",length);
if(handle < 0) lsda_perror("ACK!");
for(;;) {
  printf("%s > ",argv[1]);
  gets(cmd);
  if(strcmp(cmd,"pwd") == 0) {
     printf("%s\n",lsda_getpwd(handle));
  } else if(strcmp(cmd,"ls") == 0) {
     listdir(handle);
  } else if(strncmp(cmd,"cd ",3) == 0) {
/*
     lsda_queryvar(handle,cmd+3,&typeid,&length,&filenum);
     if(typeid < 0) {
       printf("%s does not exist\n",cmd+3);
     } else if(typeid > 0) {
       printf("%s is not a directory\n",cmd+3);
     } else {
       lsda_cd(handle,cmd+3);
     }
*/
     if(lsda_cd(handle,cmd+3) < 0) {
       printf("%s does not exist or is not a directory\n",cmd+3);
     }
  } else if(strncmp(cmd,"cat ",4) == 0) {
     printvar(handle,cmd+4);
  } else if(strncmp(cmd,"type ",5) == 0) {
     printvar(handle,cmd+5);
  } else if(strcmp(cmd,"bye") == 0 || 
            strcmp(cmd,"quit") == 0 || 
            strcmp(cmd,"done") == 0 || 
            strcmp(cmd,"exit") == 0 || 
            strcmp(cmd,"end") == 0 ) {
     lsda_close(handle);
     exit(0);
  } else if(cmd[0]) {
     printf("Unknown command %s",cmd);
     printf("Try one of these: ls, cd, cat, pwd, quit\n");
  }
}
}
void printvar(int handle,char *namein)
{
int typeid;
char name[32];
LSDA_Length length;
int filenum;
int start, end, i,j;
int *idata;
char *cdata;
float *fdata;

i = sscanf(namein,"%s %d %d",name,&start,&end);
if(i < 3) end = 0;
if(i < 2) start = 0;

lsda_queryvar(handle,name,&typeid,&length,&filenum);
if(end == 0) end = length;
if(start < 0) start = 0;
if(end > length-1) end = length-1;

if(typeid < 0) {
  printf("Variable %s not found in current directory\n",name);
  return;
}
if(typeid == 0) {
  printf("%s is a directory\n",name);
  return;
}
if(typeid <= LSDA_I1) {
  i=end-start+1;
  cdata = (char *) malloc(i+1);
  lsda_read(handle,LSDA_I1,name,start,i,cdata);
  for(j=0; j<i; j++)
    if(!isprint(cdata[j])) cdata[j] = '.';
  cdata[i]=0;
  printf("%s = \"%s\"\n",name,cdata);
  free(cdata);
} else if(typeid <= LSDA_I8) {
  idata = (int *) malloc(sizeof(int)*(end-start+1));
  lsda_read(handle,LSDA_INT,name,start,(end-start+1),idata);
  for(i=0; i<end-start+1; i++)
    printf("%s[%d] = %d\n",name,i+start,idata[i]);
  free(idata);
} else if(typeid <= LSDA_U8) {
  idata = (int *) malloc(sizeof(int)*(end-start+1));
  lsda_read(handle,LSDA_UINT,name,start,(end-start+1),idata);
  for(i=0; i<end-start+1; i++)
    printf("%s[%d] = %u\n",name,i+start,idata[i]);
  free(idata);
} else {
  fdata = (float *) malloc(sizeof(float)*(end-start+1));
  lsda_read(handle,LSDA_FLOAT,name,start,(end-start+1),fdata);
  for(i=0; i<end-start+1; i++)
    printf("%s[%d] = %g\n",name,i+start,fdata[i]);
  free(fdata);
}
return;
}
void listdir(int handle)
{
LSDADir *dp = lsda_opendir(handle,".");
char name[32], type[32];
int typeid;
LSDA_Length length;
int filenum;

if(dp == NULL) {
  printf("Can't open CWD????\n");
  return;
}

for(;;) {
  lsda_readdir(dp,name,&typeid,&length,&filenum);
  if(name[0]==0)  return ;   /* end of listing */
  if(typeid==0)
    printf("%-16s\n",name);
  else {
    build_name(type,typeid);
    printf("%-16s %-8s %8d\n",name,type,length);
  } 
}
}
void build_name(char *name,int typeid)
{
static char *names[] = {
                        "I*1","I*2","I*4","I*8",
                        "U*1","U*2","U*4","U*8",
                                    "R*4","R*8" };
strcpy(name,names[typeid-1]);
}
