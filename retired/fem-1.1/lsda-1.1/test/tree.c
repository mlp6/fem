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

void listdir(int handle);
void build_name(char *name,int typeid);

char cwd[2048];
int cwd_len=0;

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
if(handle < 0) lsda_perror("ACK!");
length = lsda_totalmemory(handle);
printf("File contains %ld bytes of data\n",length);
strcpy(cwd,"/");
cwd_len = 1;
listdir(handle);
lsda_close(handle);
}

void listdir(int handle)
{
LSDADir *dp = lsda_opendir(handle,cwd);
char name[32], type[32];
int typeid;
LSDA_Length length;
int filenum;
int printed=0;

if(dp == NULL) {
  printf("%s not a valid directory path\n",cwd);
  return;
}
for(;;) {
  lsda_readdir(dp,name,&typeid,&length,&filenum);
  if(name[0]==0)  break ;   /* end of listing */
  if(typeid!=0) {
    if(printed++ == 0) printf("\n%s:\n",cwd);
    build_name(type,typeid);
    printf("%-16s %-8s %8d\n",name,type,length);
  } 
}
for(;;) {
  lsda_readdir(dp,name,&typeid,&length,&filenum);
  if(name[0]==0)  return ;   /* end of listing */
  if(typeid==0) {
    int old_len = cwd_len;
    int nlen = strlen(name);
    if(cwd_len > 1) {
      sprintf(cwd+cwd_len,"/%s",name);
      cwd_len += 1+nlen;
    } else {
      sprintf(cwd+cwd_len,"%s",name);
      cwd_len += nlen;
    }
    listdir(handle);
    cwd_len = old_len;
    cwd[cwd_len]=0;
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
