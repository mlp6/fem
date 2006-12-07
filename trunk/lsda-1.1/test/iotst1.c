/*
  Copyright (C) 2002
  by Livermore Software Technology Corp. (LSTC)
  All rights reserved
*/
#include <stdio.h>
#include <stdlib.h>
#include "lsda.h"

#ifdef PCWIN
#define LONGLONG __int64
#else
#define LONGLONG long long
#endif

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
signed char cd[] = { -120,0,120 };
short sd[] = {-30000,-120,0,120,30000 };
unsigned short usd[] = {0,120,30000,60000};
int id[] = { -600000,-30000,-120,0,120,30000,600000 };
unsigned int uid[] = { 0,120,30000,600000,0xf100ff00 };
LONGLONG ld[] = {0xff00000000000000,
                  0x0f00000000000000,
                  0x000ff00000000000,
                  0x000000ff00000000,
                  0x00000000ff000000,
                  0x0000000000ff0000,
                  0x000000000000ff00,
                  0x00000000000000ff};
unsigned LONGLONG uld[] = {0xff00000000000000,
                            0x0f00000000000000,
                            0x000ff00000000000,
                            0x000000ff00000000,
                            0x00000000ff000000,
                            0x0000000000ff0000,
                            0x000000000000ff00,
                            0x00000000000000ff};
float fd[] = {-1.e+25,-1.,-1.e-25,0,1.e-25,1.,1.e+25};
double dd[] = {-1.e+100,-1.e+25,-1.,-1.e-25,-1.e-100,0,
               1.e-100,1.e-25,1.,1.e+25,1.e+100};
int i;

lsda_cd(handle,"/");
i = sizeof(cd)/sizeof(cd[0]);
lsda_write(handle,LSDA_I1,"cd",i,cd);
i = sizeof(sd)/sizeof(sd[0]);
lsda_write(handle,LSDA_SHORT,"sd",i,sd);
i = sizeof(usd)/sizeof(usd[0]);
lsda_write(handle,LSDA_USHORT,"usd",i,usd);
i = sizeof(id)/sizeof(id[0]);
lsda_write(handle,LSDA_INT,"id",i,id);
i = sizeof(uid)/sizeof(uid[0]);
lsda_write(handle,LSDA_UINT,"uid",i,uid);
i = sizeof(ld)/sizeof(ld[0]);
lsda_write(handle,LSDA_I8,"ld",i,ld);
i = sizeof(uld)/sizeof(uld[0]);
lsda_write(handle,LSDA_U8,"uld",i,uld);
i = sizeof(fd)/sizeof(fd[0]);
lsda_write(handle,LSDA_FLOAT,"fd",i,fd);
i = sizeof(dd)/sizeof(dd[0]);
lsda_write(handle,LSDA_DOUBLE,"dd",i,dd);
lsda_close(handle);
}
read_test(char *name)
{
typedef struct _x {
  char *name;
  int num;
} XX;
XX ints[] = { {"cd",3},
              {"sd",5},
              {"usd",4},
              {"id",7},
              {"uid",5},
              {"ld",8},
              {"uld",8}};
XX reals[]= { {"fd",7},
              {"dd",11}};
signed char cd[10];
short sd[10];
unsigned short usd[10];
int id[10];
unsigned int uid[10];
LONGLONG ld[10];
unsigned LONGLONG uld[10];
float fd[15];
double dd[15];
int i,j,k;

int handle = lsda_open(name,LSDA_READONLY);
if(handle < 0) printf("open error!\n");
#if DEBUG
lsda_dumpst(handle);
#endif
lsda_cd(handle,"/");
/*
  Try reading everything as each type
*/
for(i=0; i<7; i++) {
  lsda_read(handle,LSDA_SHORT,ints[i].name,0,ints[i].num,sd);
  for(j=0; j<ints[i].num; j++)
    printf("(short) %s[%d] = %d\n",ints[i].name,j,sd[j]);
  lsda_read(handle,LSDA_INT,ints[i].name,0,ints[i].num,id);
  for(j=0; j<ints[i].num; j++)
    printf("(int) %s[%d] = %d\n",ints[i].name,j,id[j]);
  lsda_read(handle,LSDA_I8,ints[i].name,0,ints[i].num,ld);
  for(j=0; j<ints[i].num; j++)
    printf("(I*8) %s[%d] = %lld\n",ints[i].name,j,ld[j]);
}

for(i=0; i<2; i++) {
  lsda_read(handle,LSDA_FLOAT,reals[i].name,0,reals[i].num,fd);
  for(j=0; j<reals[i].num; j++)
    printf("(float) %s[%d] = %g\n",reals[i].name,j,fd[j]);
  lsda_read(handle,LSDA_DOUBLE,reals[i].name,0,reals[i].num,dd);
  for(j=0; j<reals[i].num; j++)
    printf("(double) %s[%d] = %lg\n",reals[i].name,j,dd[j]);
}

lsda_close(handle);
}
