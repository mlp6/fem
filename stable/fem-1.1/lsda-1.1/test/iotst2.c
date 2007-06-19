/*
  Copyright (C) 2002
  by Livermore Software Technology Corp. (LSTC)
  All rights reserved
*/
#include <stdio.h>
#include <stdlib.h>
#include "lsda.h"
main(int argc, char *argv[])
{

if(argc < 3) {
  printf("syntax: %s file read/write\n",argv[0]);
  exit(1);
}
if(strcmp(argv[2],"read") == 0) {
   read_test(argv[1]);
} else {
   write_test(argv[1]);
}
}
write_test(char *name)
{
int handle = lsda_open(name,LSDA_WRITEONLY);
int data[10],i;

for(i=0; i<10; i++)
  data[i] = i;
lsda_cd(handle,"/dir1");
lsda_write(handle,LSDA_INT,"data0",10,data);


for(i=0; i<10; i++)
  data[i] = 100+i;
lsda_cd(handle,"/dir2");
lsda_write(handle,LSDA_INT,"data100",10,data);
for(i=0; i<10; i++)
  data[i] = 200+i;
lsda_write(handle,LSDA_INT,"data200",10,data);
lsda_cd(handle,"/dir1/sub1");
lsda_cd(handle,"/dir1/sub1/sub2");
lsda_write(handle,LSDA_INT,"data200",10,data);
lsda_flush(handle);
lsda_write(handle,LSDA_INT,"data201",10,data);
lsda_cd(handle,"/dir1/sub1");
lsda_write(handle,LSDA_INT,"data201",10,data);
lsda_cd(handle,"/dir1/sub2");
lsda_write(handle,LSDA_INT,"data202",10,data);
lsda_nextfile(handle);
lsda_cd(handle,"/dir1/sub1");
lsda_write(handle,LSDA_INT,"data20a",10,data);
lsda_cd(handle,"/dir1/sub2");
lsda_write(handle,LSDA_INT,"data20b",10,data);

lsda_close(handle);
}
read_test(char *name)
{
int handle;
int data[10],i;
lsda_setreportlevel(1);
handle = lsda_open(name,LSDA_READONLY);
if(lsda_errno != 0) lsda_perror("Aborting!");
#if DEBUG
lsda_dumpst(handle);
#endif
/*
  Read a couple of specific variables
*/
lsda_read(handle,LSDA_INT,"/dir1/data0",2,5,data);
for(i=0; i<5; i++)
  printf("/dir1/data0[%d] = %d\n",i+2,data[i]);
lsda_read(handle,LSDA_INT,"/dir1/sub1/sub2/data200",1,6,data);
for(i=0; i<6; i++)
  printf("/dir1/sub1/sub2/data200[%d] = %d\n",i+1,data[i]);
lsda_close(handle);
}
