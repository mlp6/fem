/*
  Copyright (C) 2002
  by Livermore Software Technology Corp. (LSTC)
  All rights reserved
*/
#include <stdlib.h>
#include <stdio.h>
#include <malloc.h>

#include "lsda.h"

main(int argc, char *argv[])
{
  int handle,i;
  int typeid, filenum;
  LSDA_Length length;
  LSDADir *dp;
  char name[32], type[32];

  if(argc < 2) {
    printf("Syntax: %s inputfile (inputfile) (inputfile)....\n",argv[0]);
    exit(1);
  }
  handle = lsda_open_many(argv+1,argc-1);
  if(handle < 0) {
    printf("One of the arguments does not appear to be a valid LSDA file\n");
    exit(1);
  }
  dp = lsda_opendir(handle,"/");

  for(;;) {
    lsda_readdir(dp,name,&typeid,&length,&filenum);
    if(name[0]==0)  break ;   /* end of listing */
    if(strcmp(name,"secforc")== 0) translate_secforc(handle);
    if(strcmp(name,"rwforc") == 0) translate_rwforc(handle);
    if(strcmp(name,"nodout") == 0) translate_nodout(handle);
    if(strcmp(name,"elout")  == 0) translate_elout(handle);
    if(strcmp(name,"glstat") == 0) translate_glstat(handle);
    if(strcmp(name,"ssstat") == 0) translate_ssstat(handle);
    if(strcmp(name,"deforc") == 0) translate_deforc(handle);
    if(strcmp(name,"matsum") == 0) translate_matsum(handle);
    if(strcmp(name,"ncforc") == 0) translate_ncforc(handle);
    if(strcmp(name,"rcforc") == 0) translate_rcforc(handle);
    if(strcmp(name,"spcforc")== 0) translate_spcforc(handle);
    if(strcmp(name,"swforc") == 0) translate_swforc(handle);
    if(strcmp(name,"abstat") == 0) translate_abstat(handle);
    if(strcmp(name,"nodfor") == 0) translate_nodfor(handle);
    if(strcmp(name,"bndout") == 0) translate_bndout(handle);
    if(strcmp(name,"rbdout") == 0) translate_rbdout(handle);
    if(strcmp(name,"gceout") == 0) translate_gceout(handle);
    if(strcmp(name,"sleout") == 0) translate_sleout(handle);
    if(strcmp(name,"sbtout") == 0) translate_sbtout(handle);
    if(strcmp(name,"jntforc")== 0) translate_jntforc(handle);
    if(strcmp(name,"sphout") == 0) translate_sphout(handle);
    if(strcmp(name,"defgeo") == 0) translate_defgeo(handle);
  }
  lsda_close(handle);
  exit(0);
}
int output_legend(int handle, FILE *fp,int first, int last)
{
  int i,typeid,filenum,*ids,num;
  char *legend;
  LSDA_Length length;

  lsda_queryvar(handle,"legend_ids",&typeid,&length,&filenum);
  num = length;
  if(num < 1) {
    if(!first && last) fprintf(fp,"\n\n");
    return 0;
  }
  ids = (int *) malloc(num*sizeof(int));
  legend = (char *) malloc(70*num);
  lsda_read(handle,LSDA_INT,"legend_ids",0,num,ids);
  lsda_read(handle,LSDA_I1,"legend",0,70*num,legend);
  if(first) {
    fprintf(fp,"\n{BEGIN LEGEND\n");
    fprintf(fp," Entity #        Title\n");
  }
  for(i=0; i<num; i++) {
    fprintf(fp,"%9d     %.70s\n",ids[i],legend+70*i);
  }
  if(last) fprintf(fp,"{END LEGEND}\n\n");
  free(legend);
  free(ids);
  return 1;
}
/*
  SECFORC file
*/
translate_secforc(int handle)
{
  int i,typeid,num,filenum,state,need_renumber;
  LSDA_Length length;
  char dirname[128];
  char title[81];
  char version[11];
  char date[11];
  int *ids, *idfix;
  int *rigidbody;
  int *accelerometer;
  float time;
  float *x_force;
  float *y_force;
  float *z_force;
  float *total_force;
  float *x_moment;
  float *y_moment;
  float *z_moment;
  float *total_moment;
  float *x_centroid;
  float *y_centroid;
  float *z_centroid;
  float *area;
  FILE *fp;

  lsda_cd(handle,"/secforc/metadata");
  printf("Extracting SECFORC data\n");
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num=length;

/*
  allocate memory to read in 1 state
*/
  ids = (int *) malloc(num*sizeof(int));
  rigidbody = (int *) malloc(num*sizeof(int));
  accelerometer = (int *) malloc(num*sizeof(int));
  x_force = (float *) malloc(num*sizeof(float));
  y_force = (float *) malloc(num*sizeof(float));
  z_force = (float *) malloc(num*sizeof(float));
  total_force = (float *) malloc(num*sizeof(float));
  x_moment = (float *) malloc(num*sizeof(float));
  y_moment = (float *) malloc(num*sizeof(float));
  z_moment = (float *) malloc(num*sizeof(float));
  total_moment = (float *) malloc(num*sizeof(float));
  x_centroid = (float *) malloc(num*sizeof(float));
  y_centroid = (float *) malloc(num*sizeof(float));
  z_centroid = (float *) malloc(num*sizeof(float));
  area = (float *) malloc(num*sizeof(float));
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
  /*
   * There is a bug in some of the earlier releases of DYNA, whereby the
   * MPP code assigns the wrong ids to the cross sections: each processor
   * numbers their own from 1-n locally.  The result is that the id numbers
   * actually written can be wrong.  The actual data is correct, and in the
   * correct order.  So, if we can detect this condition, we will just
   * renumber them here from 1 to num.  In the broken code, each section
   * gets, as its id, the max of its ids on all the processors it lives on.
   * The only thing we can reliably look for is collisions.  If there are
   * no collisions, there is no why to be SURE the data is not correct.
   * But watch for ids > num, in case the user assigned IDs (which are
   * honored, even in the broken code).
   */
  idfix = rigidbody;   /* use this as scratch space. */
  memset(idfix,0,num*sizeof(int));
  need_renumber = 0;
  for(i=0; i<num; i++) {
    if(ids[i] > 0 && ids[i] <= num) {
      if(++idfix[ids[i]-1] > 1)
        need_renumber=1;
    }
  }
  if(need_renumber) {
    for(i=0; i<num; i++) {
      if(ids[i] > 0 && ids[i] <= num)  /* leave user given IDS alone... */
        ids[i]=i+1;
    }
  }
  lsda_read(handle,LSDA_INT,"rigidbody",0,num,rigidbody);
  lsda_read(handle,LSDA_INT,"accelerometer",0,num,accelerometer);
/*
  open file and write header
*/
  fp=fopen("secforc","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  output_legend(handle,fp,1,1);
  fprintf(fp,"\n\n");
  fprintf(fp," line#1  section#     time        x-force     y-force     z-force    magnitude\n");
  fprintf(fp," line#2  resultant  moments       x-moment    y-moment    z-moment   magnitude\n");
  fprintf(fp," line#3  centroids                x           y           z            area  \n");

/*
  Loop through time states and write each one
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/secforc/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_force",0,num,x_force) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_force",0,num,y_force) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_force",0,num,z_force) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"total_force",0,num,total_force) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_moment",0,num,x_moment) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_moment",0,num,y_moment) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_moment",0,num,z_moment) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"total_moment",0,num,total_moment) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_centroid",0,num,x_centroid) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_centroid",0,num,y_centroid) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_centroid",0,num,z_centroid) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"area",0,num,area) != num) break;
    for(i=0; i<num; i++) {
      fprintf(fp,"%12d%15.5E",ids[i],time);
      fprintf(fp,"%15.4E%12.4E%12.4E%12.4E\n",x_force[i],y_force[i],z_force[i],total_force[i]);
      if(rigidbody[i] != 0) {
        fprintf(fp,"rb ID =%8d            ",rigidbody[i]);
      } else if(accelerometer[i] != 0) {
        fprintf(fp,"ac ID =%8d            ",accelerometer[i]);
      } else {
        fprintf(fp,"global system              ");
      }
      fprintf(fp,"%15.4E%12.4E%12.4E%12.4E\n",x_moment[i],y_moment[i],z_moment[i],total_moment[i]);
      fprintf(fp,"                           ");
      fprintf(fp,"%15.4E%12.4E%12.4E%12.4E\n\n",x_centroid[i],y_centroid[i],z_centroid[i],area[i]);
    }
  }
  fclose(fp);
  free(area);
  free(z_centroid);
  free(y_centroid);
  free(x_centroid);
  free(total_moment);
  free(z_moment);
  free(y_moment);
  free(x_moment);
  free(total_force);
  free(z_force);
  free(y_force);
  free(x_force);
  free(accelerometer);
  free(rigidbody);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  RWFORC file
*/
translate_rwforc(int handle)
{
  int i,j,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[128];
  char title[81];
  char version[11];
  char date[11];
  int *ids;
  int *nwalls,maxwall;
  int cycle;
  float time;
  float *fx,*fy,*fz,*fn;
  float *sfx,*sfy,*sfz,tx,ty,tz;
  FILE *fp;

  printf("Extracting RWFORC data\n");
  lsda_cd(handle,"/rwforc/forces/metadata");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;

  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num=length;
  ids    = (int *) malloc(num*sizeof(int));
  nwalls = (int *) malloc(num*sizeof(int));
  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
/*
  allocate memory to read in 1 state
*/
  fx   = (float *) malloc(num*sizeof(float));
  fy   = (float *) malloc(num*sizeof(float));
  fz   = (float *) malloc(num*sizeof(float));
  fn   = (float *) malloc(num*sizeof(float));
/*
  see which if any walls have segments defined for them...
*/
  for(i=maxwall=0; i<num; i++) {
    sprintf(dirname,"/rwforc/wall%3.3d/metadata/ids",i+1);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid > 0)
      nwalls[i] = length;
    else
      nwalls[i] = 0;
    if(maxwall < nwalls[i]) maxwall=nwalls[i];
  }
  if(maxwall > 0) {
    sfx   = (float *) malloc(maxwall*sizeof(float));
    sfy   = (float *) malloc(maxwall*sizeof(float));
    sfz   = (float *) malloc(maxwall*sizeof(float));
  }
/*
  open file and write header
*/
  fp=fopen("rwforc","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  output_legend(handle,fp,1,1);
  fprintf(fp,"\n\n");
  fprintf(fp,"    time       wall#   normal-force    x-force        y-force        z-force\n");
/*
  Loop through time states and write each one
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/rwforc/forces/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_force",0,num,fx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_force",0,num,fy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_force",0,num,fz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"normal_force",0,num,fn) != num) break;
    for(i=0; i<num; i++) {
      fprintf(fp,"%12.5E%8d%15.6E%15.6E%15.6E%15.6E\n",
        time,ids[i],fn[i],fx[i],fy[i],fz[i]);
      if(nwalls[i] > 0) {
        sprintf(dirname,"/rwforc/wall%3.3d/d%6.6d",i+1,state);
        lsda_cd(handle,dirname);
        if(lsda_read(handle,LSDA_FLOAT,"x_force",0,nwalls[i],sfx) != nwalls[i]) break;
        if(lsda_read(handle,LSDA_FLOAT,"y_force",0,nwalls[i],sfy) != nwalls[i]) break;
        if(lsda_read(handle,LSDA_FLOAT,"z_force",0,nwalls[i],sfz) != nwalls[i]) break;
        if(lsda_read(handle,LSDA_FLOAT,"total_x",0,1,&tx) != 1) break;
        if(lsda_read(handle,LSDA_FLOAT,"total_y",0,1,&ty) != 1) break;
        if(lsda_read(handle,LSDA_FLOAT,"total_z",0,1,&tz) != 1) break;
        fprintf(fp,"                seg#    \n");
        for(j=0; j<nwalls[i]; j++) {
          fprintf(fp,"            %8d               %15.6E%15.6E%15.6E\n",
            j+1,sfx[j],sfy[j],sfz[j]);
        }
        fprintf(fp,"  total force                      %15.6E%15.6E%15.6E\n",
            tx,ty,tz);
      }
    }
  }
  fclose(fp);
  if(maxwall > 0) {
    free(sfz);
    free(sfy);
    free(sfz);
  }
  free(fn);
  free(fz);
  free(fy);
  free(fx);
  free(nwalls);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  NODOUT file
*/
translate_nodout(int handle)
{
  int i,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[128];
  char title[81];
  char version[11];
  char date[11];
  int *ids;
  int cycle,have_rot;
  float time;
  float *x,*y,*z;
  float *x_d,*y_d,*z_d;
  float *x_v,*y_v,*z_v;
  float *x_a,*y_a,*z_a;
  FILE *fp;

  lsda_cd(handle,"/nodout/metadata");
  printf("Extracting NODOUT data\n");
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num=length;

/*
  allocate memory to read in 1 state
*/
  ids = (int *) malloc(num*sizeof(int));
  x   = (float *) malloc(num*sizeof(float));
  y   = (float *) malloc(num*sizeof(float));
  z   = (float *) malloc(num*sizeof(float));
  x_d = (float *) malloc(num*sizeof(float));
  y_d = (float *) malloc(num*sizeof(float));
  z_d = (float *) malloc(num*sizeof(float));
  x_v = (float *) malloc(num*sizeof(float));
  y_v = (float *) malloc(num*sizeof(float));
  z_v = (float *) malloc(num*sizeof(float));
  x_a = (float *) malloc(num*sizeof(float));
  y_a = (float *) malloc(num*sizeof(float));
  z_a = (float *) malloc(num*sizeof(float));
  lsda_queryvar(handle,"../d000001/rx_displacement",&typeid,&length,&filenum);
  if(typeid > 0) {
    have_rot = 1;
  } else {
    have_rot = 0;
  }
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
/*
  open file and write header
*/
  fp=fopen("nodout","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  output_legend(handle,fp,1,1);
/*
  Loop through time states and write each one
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/nodout/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_INT,"cycle",0,1,&cycle) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_displacement",0,num,x_d) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_displacement",0,num,y_d) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_displacement",0,num,z_d) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_velocity",0,num,x_v) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_velocity",0,num,y_v) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_velocity",0,num,z_v) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_acceleration",0,num,x_a) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_acceleration",0,num,y_a) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_acceleration",0,num,z_a) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_coordinate",0,num,x) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_coordinate",0,num,y) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_coordinate",0,num,z) != num) break;

    fprintf(fp,"\n\n\n n o d a l   p r i n t   o u t   f o r   t i m e  ");
    fprintf(fp,"s t e p%8d                              ( at time%12.5E )\n",cycle,time);
    fprintf(fp,"\n nodal point  x-disp     y-disp      z-disp      ");
    fprintf(fp,"x-vel       y-vel       z-vel      x-accl      y-accl      ");
    fprintf(fp,"z-accl      x-coor      y-coor      z-coor\n");
    for(i=0; i<num; i++) {
      fprintf(fp,"%9d%13.4E%12.4E%12.4E",ids[i],x_d[i],y_d[i],z_d[i]);
      fprintf(fp,"%12.4E%12.4E%12.4E",x_v[i],y_v[i],z_v[i]);
      fprintf(fp,"%12.4E%12.4E%12.4E",x_a[i],y_a[i],z_a[i]);
      fprintf(fp,"%12.4E%12.4E%12.4E\n",x[i],y[i],z[i]);
    }
    if(have_rot) {
      if(lsda_read(handle,LSDA_FLOAT,"rx_displacement",0,num,x_d) != num) break;
      if(lsda_read(handle,LSDA_FLOAT,"ry_displacement",0,num,y_d) != num) break;
      if(lsda_read(handle,LSDA_FLOAT,"rz_displacement",0,num,z_d) != num) break;
      if(lsda_read(handle,LSDA_FLOAT,"rx_velocity",0,num,x_v) != num) break;
      if(lsda_read(handle,LSDA_FLOAT,"ry_velocity",0,num,y_v) != num) break;
      if(lsda_read(handle,LSDA_FLOAT,"rz_velocity",0,num,z_v) != num) break;
      if(lsda_read(handle,LSDA_FLOAT,"rx_acceleration",0,num,x_a) != num) break;
      if(lsda_read(handle,LSDA_FLOAT,"ry_acceleration",0,num,y_a) != num) break;
      if(lsda_read(handle,LSDA_FLOAT,"rz_acceleration",0,num,z_a) != num) break;

      fprintf(fp,"\n\n\n n o d a l   p r i n t   o u t   f o r   t i m e  ");
      fprintf(fp,"s t e p%8d                              ( at time%12.5E )\n",cycle,time);
      fprintf(fp,"\n nodal point  x-rot      y-rot       z-rot       ");
      fprintf(fp,"x-rot vel   y-rot vel   z-rot vel   x-rot acc   y-rot acc   ");
      fprintf(fp,"z-rot acc\n");
      for(i=0; i<num; i++) {
        fprintf(fp,"%9d%13.4E%12.4E%12.4E",ids[i],x_d[i],y_d[i],z_d[i]);
        fprintf(fp,"%12.4E%12.4E%12.4E",x_v[i],y_v[i],z_v[i]);
        fprintf(fp,"%12.4E%12.4E%12.4E\n",x_a[i],y_a[i],z_a[i]);
      }
    }
  }
  fclose(fp);
  free(z_a);
  free(y_a);
  free(x_a);
  free(z_v);
  free(y_v);
  free(x_v);
  free(z_d);
  free(y_d);
  free(x_d);
  free(z);
  free(y);
  free(x);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  ELOUT file
*/
typedef struct {
  char title[84];
  char version[12];
  char date[12];
  char states[20][32];
  int idsize;
  int *ids,*mat,*state;
  float *sxx,*syy,*szz,*sxy,*syz,*szx,*yield,*effsg;
} MDSOLID;
typedef struct {
  char title[84];
  char version[12];
  char date[12];
  char states[20][32];
  char system[8];
} MDTSHELL;
typedef struct {
  char title[84];
  char version[12];
  char date[12];
  int idsize, dsize;
  int *ids, *mat, *nip;
  float *axial, *shears, *sheart, *moments, *momentt, *torsion;
  float *s11,*s12,*s31,*plastic;
} MDBEAM;
typedef struct {
  char title[84];
  char version[12];
  char date[12];
  char states[20][32];
  char system[8];
  int idsize, dsize;
  int *ids, *mat, *nip, *state, *iop;
  float *sxx, *syy, *szz;
  float *sxy, *syz, *szx;
  float *ps;
  float *lxx, *lyy, *lzz;
  float *lxy, *lyz, *lzx;
  float *uxx, *uyy, *uzz;
  float *uxy, *uyz, *uzx;
} MDSHELL;

translate_elout(int handle)
{
  int i,j,k,typeid,filenum,state;
  LSDA_Length length;
  char dirname[256];
  int have_solid, have_tshell, have_beam, have_shell;
  FILE *fp;
  MDSOLID solid;
  MDTSHELL tshell;
  MDBEAM beam;
  MDSHELL shell;
  char *title=NULL, *version, *date;

  lsda_queryvar(handle,"/elout/solid",&typeid,&length,&filenum);
  have_solid= (typeid >= 0);
  lsda_queryvar(handle,"/elout/thickshell",&typeid,&length,&filenum);
  have_tshell= (typeid >= 0);
  lsda_queryvar(handle,"/elout/beam",&typeid,&length,&filenum);
  have_beam= (typeid >= 0);
  lsda_queryvar(handle,"/elout/shell",&typeid,&length,&filenum);
  have_shell= (typeid >= 0);

/*
  Read metadata

  Solids
*/
  if(have_solid) {
    lsda_cd(handle,"/elout/solid/metadata");
    lsda_read(handle,LSDA_I1,"title",0,80,solid.title);
    solid.title[72]=0;
    lsda_read(handle,LSDA_I1,"version",0,10,solid.version);
    solid.version[10]=0;
    lsda_read(handle,LSDA_I1,"date",0,10,solid.date);
    solid.date[10]=0;
    lsda_queryvar(handle,"states",&typeid,&length,&filenum);
    lsda_read(handle,LSDA_I1,"states",0,length,dirname);
    for(i=j=k=0; i<length; i++) {
      if(dirname[i] == ',') {
        solid.states[j][k]=0;
        j++;
        k=0;
      } else {
        solid.states[j][k++]=dirname[i];
      }
    }
    solid.states[j][k]=0;
    title = solid.title;
    version = solid.version;
    date = solid.date;
    solid.idsize = -1;
    solid.ids = NULL;
  }
/*
  thick shells
*/
  if(have_tshell) {
    lsda_cd(handle,"/elout/thickshell/metadata");
    lsda_read(handle,LSDA_I1,"title",0,80,tshell.title);
    tshell.title[72]=0;
    lsda_read(handle,LSDA_I1,"version",0,10,tshell.version);
    tshell.version[10]=0;
    lsda_read(handle,LSDA_I1,"date",0,10,tshell.date);
    tshell.date[10]=0;
    lsda_queryvar(handle,"states",&typeid,&length,&filenum);
    lsda_read(handle,LSDA_I1,"states",0,length,dirname);
    for(i=j=k=0; i<length; i++) {
      if(dirname[i] == ',') {
        tshell.states[j][k]=0;
        j++;
        k=0;
      } else {
        tshell.states[j][k++]=dirname[i];
      }
    }
    tshell.states[j][k]=0;
    lsda_read(handle,LSDA_I1,"system",0,6,tshell.system);
    tshell.system[6]=0;
    title = tshell.title;
    version = tshell.version;
    date = tshell.date;
  }
/*
  beams
*/
  if(have_beam) {
    lsda_cd(handle,"/elout/beam/metadata");
    lsda_read(handle,LSDA_I1,"title",0,80,beam.title);
    beam.title[72]=0;
    lsda_read(handle,LSDA_I1,"version",0,10,beam.version);
    beam.version[10]=0;
    lsda_read(handle,LSDA_I1,"date",0,10,beam.date);
    beam.date[10]=0;
    title = beam.title;
    version = beam.version;
    date = beam.date;
    beam.idsize = -1;
    beam.dsize = -1;
    beam.ids = NULL;
    beam.s11 = NULL;
  }
/*
  shells
*/
  if(have_shell) {
    lsda_cd(handle,"/elout/shell/metadata");
    lsda_read(handle,LSDA_I1,"title",0,80,shell.title);
    shell.title[72]=0;
    lsda_read(handle,LSDA_I1,"version",0,10,shell.version);
    shell.version[10]=0;
    lsda_read(handle,LSDA_I1,"date",0,10,shell.date);
    shell.date[10]=0;
    lsda_queryvar(handle,"states",&typeid,&length,&filenum);
    lsda_read(handle,LSDA_I1,"states",0,length,dirname);
    for(i=j=k=0; i<length; i++) {
      if(dirname[i] == ',') {
        shell.states[j][k]=0;
        j++;
        k=0;
      } else {
        shell.states[j][k++]=dirname[i];
      }
    }
    shell.states[j][k]=0;
    lsda_read(handle,LSDA_I1,"system",0,6,shell.system);
    shell.system[6]=0;
    for(i=5; i>0 && shell.system[i] == ' '; i--)
      shell.system[i]=0;
    title = shell.title;
    version = shell.version;
    date = shell.date;
    shell.idsize = -1;
    shell.dsize = -1;
    shell.ids = NULL;
    shell.lxx = NULL;
    shell.sxx = NULL;
  }

  if(title == NULL) return;  /* huh? */
/*
  open file and write header
*/
  printf("Extracting ELOUT data\n");
  fp=fopen("elout","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  k = 0;
  if(have_solid) {
    lsda_cd(handle,"/elout/solid/metadata");
    i = (have_tshell | have_beam | have_shell) ? 0 : 1;
    k = output_legend(handle,fp,1,i);
  }
  if(have_tshell) {
    lsda_cd(handle,"/elout/thickshell/metadata");
    i = !k;
    j = (have_beam | have_shell) ? 0 : 1;
    k = output_legend(handle,fp,i,j) || k;
  }
  if(have_beam) {
    lsda_cd(handle,"/elout/beam/metadata");
    i = !k;
    j = (have_shell) ? 0 : 1;
    k = output_legend(handle,fp,i,j) || k;
  }
  if(have_shell) {
    lsda_cd(handle,"/elout/shell/metadata");
    i = !k;
    output_legend(handle,fp,i,1);
  }
/*
  Loop through time states and write each one
*/
  for(state=1;have_solid || have_tshell || have_beam || have_shell ; state++) {
    if(have_solid) {
      if(! elout_solid(fp,handle,state,&solid)) {
        if(solid.ids) {
          free(solid.ids);
          free(solid.mat);
          free(solid.state);
          free(solid.sxx);
          free(solid.syy);
          free(solid.szz);
          free(solid.sxy);
          free(solid.syz);
          free(solid.szx);
          free(solid.yield);
          free(solid.effsg);
        }
        have_solid = 0;
      }
    }
    if(have_tshell) {
      if(! elout_tshell(fp,handle,state,&tshell)) {
        have_tshell = 0;
      }
    }
    if(have_beam) {
      if(! elout_beam(fp,handle,state,&beam)) {
        if(beam.ids) {
          free(beam.ids);
          free(beam.mat);
          free(beam.nip);
          free(beam.axial);
          free(beam.shears);
          free(beam.sheart);
          free(beam.moments);
          free(beam.momentt);
          free(beam.torsion);
          if(beam.s11) {
            free(beam.s11);
            free(beam.s12);
            free(beam.s31);
            free(beam.plastic);
          }
        }
        have_beam = 0;
      }
    }
    if(have_shell) {
      if(! elout_shell(fp,handle,state,&shell)) {
        if(shell.ids) {
          free(shell.ids);
          free(shell.mat);
          free(shell.nip);
          free(shell.state);
          free(shell.iop);
          if(shell.lxx) {
            free(shell.lxx);
            free(shell.lyy);
            free(shell.lzz);
            free(shell.lxy);
            free(shell.lyz);
            free(shell.lzx);
            free(shell.uxx);
            free(shell.uyy);
            free(shell.uzz);
            free(shell.uxy);
            free(shell.uyz);
            free(shell.uzx);
          }
          free(shell.sxx);
          free(shell.syy);
          free(shell.szz);
          free(shell.sxy);
          free(shell.syz);
          free(shell.szx);
          free(shell.ps);
        }
        have_shell=0;
      }
    }
  }
  close(fp);
/*
  free everything here....
*/
  if(have_solid && solid.ids) {
    free(solid.ids);
    free(solid.mat);
    free(solid.state);
    free(solid.sxx);
    free(solid.syy);
    free(solid.szz);
    free(solid.sxy);
    free(solid.syz);
    free(solid.szx);
    free(solid.yield);
    free(solid.effsg);
  }
  if(have_beam && beam.ids) {
    free(beam.ids);
    free(beam.mat);
    free(beam.nip);
    free(beam.axial);
    free(beam.shears);
    free(beam.sheart);
    free(beam.moments);
    free(beam.momentt);
    free(beam.torsion);
    if(beam.s11) {
      free(beam.s11);
      free(beam.s12);
      free(beam.s31);
      free(beam.plastic);
    }
  }
  if(have_shell && shell.ids) {
    free(shell.ids);
    free(shell.mat);
    free(shell.nip);
    free(shell.state);
    free(shell.iop);
    if(shell.lxx) {
      free(shell.lxx);
      free(shell.lyy);
      free(shell.lzz);
      free(shell.lxy);
      free(shell.lyz);
      free(shell.lzx);
      free(shell.uxx);
      free(shell.uyy);
      free(shell.uzz);
      free(shell.uxy);
      free(shell.uyz);
      free(shell.uzx);
    }
    free(shell.sxx);
    free(shell.syy);
    free(shell.szz);
    free(shell.sxy);
    free(shell.syz);
    free(shell.szx);
    free(shell.ps);
  }
  printf("      %d states extracted\n",state-1);
}

elout_solid(FILE *fp,int handle, int state, MDSOLID *solid)
{
  char dirname[128];
  float time;
  int cycle;
  int typeid, filenum;
  LSDA_Length length;
  int num;
  int have_strain,i,j,k,len2;

  sprintf(dirname,"/elout/solid/d%6.6d",state);
  lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
  if(typeid != 0) return 0;
  lsda_cd(handle,dirname);
  lsda_queryvar(handle,"eps_xx",&typeid,&length,&filenum);
  have_strain = (typeid > 0);
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  if(typeid < 0) return 0;  /* all elements deleted */
  num=length;
  if(num > solid->idsize) {
    if(solid->ids) {
      free(solid->ids);
      free(solid->mat);
      free(solid->state);
      free(solid->sxx);
      free(solid->syy);
      free(solid->szz);
      free(solid->sxy);
      free(solid->syz);
      free(solid->szx);
      free(solid->yield);
      free(solid->effsg);
    }
    solid->ids = (int *) malloc(num*sizeof(int));
    solid->mat = (int *) malloc(num*sizeof(int));
    solid->state = (int *) malloc(num*sizeof(int));
    solid->sxx = (float *) malloc(num*sizeof(float));
    solid->syy = (float *) malloc(num*sizeof(float));
    solid->szz = (float *) malloc(num*sizeof(float));
    solid->sxy = (float *) malloc(num*sizeof(float));
    solid->syz = (float *) malloc(num*sizeof(float));
    solid->szx = (float *) malloc(num*sizeof(float));
    solid->yield = (float *) malloc(num*sizeof(float));
    solid->effsg = (float *) malloc(num*sizeof(float));
    solid->idsize = num;
  }
  if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) return 0;
  if(lsda_read(handle,LSDA_INT,"cycle",0,1,&cycle) != 1) return 0;
  if(lsda_read(handle,LSDA_INT,"ids",0,length,solid->ids) != length) return 0;
  if(lsda_read(handle,LSDA_INT,"mtype",0,length,solid->mat) != length) return 0;
  if(lsda_read(handle,LSDA_INT,"state",0,length,solid->state) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_xx",0,length,solid->sxx) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_yy",0,length,solid->syy) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_zz",0,length,solid->szz) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_xy",0,length,solid->sxy) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_yz",0,length,solid->syz) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_zx",0,length,solid->szx) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"yield",0,length,solid->yield) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"effsg",0,length,solid->effsg) != length) return 0;
/*
  Output stress data
*/
  fprintf(fp,"\n\n\n e l e m e n t   s t r e s s   c a l c u l a t i o n s");
  fprintf(fp,"   f o r   t i m e  s t e p%9d   ( at time%12.5E )\n\n",cycle,time);
  fprintf(fp," element  materl\n");
  fprintf(fp,"     ipt  stress       sig-xx      sig-yy      sig");
  fprintf(fp,"-zz      sig-xy      sig-yz      sig-zx           ");
  fprintf(fp,"            yield\n           state                    ");
  fprintf(fp,"                                                              ");
  fprintf(fp,"effsg      function\n");

  for(i=0; i<length; i++) {
    fprintf(fp,"%8d-%7d\n",solid->ids[i],solid->mat[i]);
    fprintf(fp,"       1 %-7s ",solid->states[solid->state[i]-1]);
    fprintf(fp,"%12.4E%12.4E%12.4E",solid->sxx[i],solid->syy[i],solid->szz[i]);
    fprintf(fp,"%12.4E%12.4E%12.4E%14.4E%14.4E\n",solid->sxy[i],solid->syz[i],
                                   solid->szx[i],solid->effsg[i],solid->yield[i]);
  }
  if(have_strain) {
    if(lsda_read(handle,LSDA_FLOAT,"eps_xx",0,length,solid->sxx) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"eps_yy",0,length,solid->syy) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"eps_zz",0,length,solid->szz) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"eps_xy",0,length,solid->sxy) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"eps_yz",0,length,solid->syz) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"eps_zx",0,length,solid->szx) != length) return 0;

    fprintf(fp,"\n\n\n e l e m e n t   s t r a i n   c a l c u l a t i o n s");
    fprintf(fp,"   f o r   t i m e  s t e p%9d   ( at time%12.5E )\n\n",cycle,time);
    fprintf(fp," element  materl\n");
    fprintf(fp," element  strain       eps-xx      eps-yy      eps");
    fprintf(fp,"-zz      eps-xy      eps-yz      eps-zx           ");
    fprintf(fp,"            yield\n num/ipt   state\n");
/*
  yield?  But nothing is printed out there....ack!
*/
    for(i=0; i<length; i++) {
      fprintf(fp,"%8d-%7d\n",solid->ids[i],solid->mat[i]);
      fprintf(fp,"      1  %-7s ",solid->states[solid->state[i]-1]);
      fprintf(fp,"%12.4E%12.4E%12.4E",solid->sxx[i],solid->syy[i],solid->szz[i]);
      fprintf(fp,"%12.4E%12.4E%12.4E\n",solid->sxy[i],solid->syz[i],solid->szx[i]);
    }
  }
  return 1;
}
elout_tshell(FILE *fp,int handle, int state, MDTSHELL *tshell)
{
  return 0;
}
elout_beam(FILE *fp,int handle, int state, MDBEAM *beam)
{
  char dirname[128];
  float time;
  int cycle;
  int typeid, filenum;
  LSDA_Length length;
  int have_strain,i,j,k,len2;

  sprintf(dirname,"/elout/beam/d%6.6d",state);
  lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
  if(typeid != 0) return 0;
  lsda_cd(handle,dirname);
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  if(typeid < 0) return 0;
  if((int) length > beam->idsize) {
    if(beam->ids) {
      free(beam->ids);
      free(beam->mat);
      free(beam->nip);
      free(beam->axial);
      free(beam->shears);
      free(beam->sheart);
      free(beam->moments);
      free(beam->momentt);
      free(beam->torsion);
    }
    beam->ids = (int *) malloc(length*sizeof(int));
    beam->mat = (int *) malloc(length*sizeof(int));
    beam->nip = (int *) malloc(length*sizeof(int));
    beam->axial = (float *) malloc(length*sizeof(float));
    beam->shears = (float *) malloc(length*sizeof(float));
    beam->sheart = (float *) malloc(length*sizeof(float));
    beam->moments = (float *) malloc(length*sizeof(float));
    beam->momentt = (float *) malloc(length*sizeof(float));
    beam->torsion = (float *) malloc(length*sizeof(float));
    beam->idsize = length;
  }
  if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) return 0;
  if(lsda_read(handle,LSDA_INT,"cycle",0,1,&cycle) != 1) return 0;
  if(lsda_read(handle,LSDA_INT,"ids",0,length,beam->ids) != length) return 0;
  if(lsda_read(handle,LSDA_INT,"mat",0,length,beam->mat) != length) return 0;
  if(lsda_read(handle,LSDA_INT,"nip",0,length,beam->nip) != length) return 0;
  for(i=len2=0; i < length; i++)
    len2 += beam->nip[i];
  if(len2 && len2 > beam->dsize) {
    if(beam->s11) {
      free(beam->s11);
      free(beam->s12);
      free(beam->s31);
      free(beam->plastic);
    }
    beam->s11 = (float *) malloc(len2*sizeof(float));
    beam->s12 = (float *) malloc(len2*sizeof(float));
    beam->s31 = (float *) malloc(len2*sizeof(float));
    beam->plastic = (float *) malloc(len2*sizeof(float));
    beam->dsize = len2;
  }
  if(lsda_read(handle,LSDA_FLOAT,"axial",0,length,beam->axial) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"shear_s",0,length,beam->shears) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"shear_t",0,length,beam->sheart) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"moment_s",0,length,beam->moments) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"moment_t",0,length,beam->momentt) != length) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"torsion",0,length,beam->torsion) != length) return 0;
  if(len2) {
    if(lsda_read(handle,LSDA_FLOAT,"sigma_11",0,len2,beam->s11) != len2) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"sigma_12",0,len2,beam->s12) != len2) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"sigma_31",0,len2,beam->s31) != len2) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"plastic_eps",0,len2,beam->plastic) != len2) return 0;
  }
/*
  Output this data
*/
  fprintf(fp,"\n\n\n\n r e s u l t a n t s   a n d   s t r e s s e s   ");
  fprintf(fp,"f o r   t i m e  s t e p%9d   ( at time%12.5E )\n",cycle,time);

  for(i=k=0; i<length; i++) {
    fprintf(fp,"\n\n\n\n beam/truss # =%8d      material #  =%5d\n",
      beam->ids[i],beam->mat[i]);
    fprintf(fp,"\n\n resultants      axial    shear-s    she");
    fprintf(fp,"ar-t    moment-s   moment-t   torsion\n");
    fprintf(fp,"           %11.3E%11.3E%11.3E",beam->axial[i],beam->shears[i],beam->sheart[i]);
    fprintf(fp,"%11.3E%11.3E%11.3E\n",beam->moments[i],beam->momentt[i],beam->torsion[i]);
    if(beam->nip[i]) {
      fprintf(fp,"\n\n integration point stresses\n");
      fprintf(fp,"                       ");
      fprintf(fp,"sigma 11       sigma 12       sigma 31   plastic  eps\n");
      for(j=0; j<beam->nip[i]; j++,k++)
        fprintf(fp,"%5d           %15.6E%15.6E%15.6E%15.6E\n",j+1,
         beam->s11[k],beam->s12[k],beam->s31[k],beam->plastic[k]);
    }
  }
  return 1;
}
elout_shell(FILE *fp,int handle, int state, MDSHELL *shell)
{
  char dirname[128];
  float time;
  int cycle;
  int typeid, filenum;
  LSDA_Length length,length2;
  int have_strain,i,j,k,len2;

  sprintf(dirname,"/elout/shell/d%6.6d",state);
  lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
  if(typeid != 0) return 0;
  lsda_cd(handle,dirname);
  lsda_queryvar(handle,"lower_eps_xx",&typeid,&length2,&filenum);
  have_strain = (typeid > 0);
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  if(typeid < 0) return 0;
  if((int) length > shell->idsize) {
    if(shell->ids) {
      free(shell->ids);
      free(shell->mat);
      free(shell->nip);
      free(shell->iop);
      if(have_strain) {
        free(shell->lxx);
        free(shell->lyy);
        free(shell->lzz);
        free(shell->lxy);
        free(shell->lyz);
        free(shell->lzx);
        free(shell->uxx);
        free(shell->uyy);
        free(shell->uzz);
        free(shell->uxy);
        free(shell->uyz);
        free(shell->uzx);
      }
    }
    shell->ids = (int *) malloc(length*sizeof(int));
    shell->mat = (int *) malloc(length*sizeof(int));
    shell->nip = (int *) malloc(length*sizeof(int));
    shell->iop = (int *) malloc(length*sizeof(int));
    if(have_strain) {
      shell->lxx = (float *) malloc(length*sizeof(float));
      shell->lyy = (float *) malloc(length*sizeof(float));
      shell->lzz = (float *) malloc(length*sizeof(float));
      shell->lxy = (float *) malloc(length*sizeof(float));
      shell->lyz = (float *) malloc(length*sizeof(float));
      shell->lzx = (float *) malloc(length*sizeof(float));
      shell->uxx = (float *) malloc(length*sizeof(float));
      shell->uyy = (float *) malloc(length*sizeof(float));
      shell->uzz = (float *) malloc(length*sizeof(float));
      shell->uxy = (float *) malloc(length*sizeof(float));
      shell->uyz = (float *) malloc(length*sizeof(float));
      shell->uzx = (float *) malloc(length*sizeof(float));
    }
    shell->idsize = length;
  }
  if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) return 0;
  if(lsda_read(handle,LSDA_INT,"cycle",0,1,&cycle) != 1) return 0;
  if(lsda_read(handle,LSDA_INT,"ids",0,length,shell->ids) != length) return 0;
  if(lsda_read(handle,LSDA_INT,"mat",0,length,shell->mat) != length) return 0;
  if(lsda_read(handle,LSDA_INT,"nip",0,length,shell->nip) != length) return 0;
  if(lsda_read(handle,LSDA_INT,"iop",0,length,shell->iop) != length) return 0;
  for(i=len2=0; i < length; i++)
    len2 += shell->nip[i];
  if(len2 > shell->dsize) {
    if(shell->sxx) {
      free(shell->state);
      free(shell->sxx);
      free(shell->syy);
      free(shell->szz);
      free(shell->sxy);
      free(shell->syz);
      free(shell->szx);
      free(shell->ps);
    }
    shell->state = (int *) malloc(len2*sizeof(int));
    shell->sxx = (float *) malloc(len2*sizeof(float));
    shell->syy = (float *) malloc(len2*sizeof(float));
    shell->szz = (float *) malloc(len2*sizeof(float));
    shell->sxy = (float *) malloc(len2*sizeof(float));
    shell->syz = (float *) malloc(len2*sizeof(float));
    shell->szx = (float *) malloc(len2*sizeof(float));
    shell->ps  = (float *) malloc(len2*sizeof(float));
    shell->dsize = len2;
  }
  if(lsda_read(handle,LSDA_INT,"state",0,len2,shell->state) != len2) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_xx",0,len2,shell->sxx) != len2) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_yy",0,len2,shell->syy) != len2) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_zz",0,len2,shell->szz) != len2) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_xy",0,len2,shell->sxy) != len2) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_yz",0,len2,shell->syz) != len2) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"sig_zx",0,len2,shell->szx) != len2) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"plastic_strain",0,len2,shell->ps) != len2) return 0;
/*
  Output this data
*/
  fprintf(fp,"\n\n\n e l e m e n t   s t r e s s   c a l c u l a t i o n s");
  fprintf(fp,"   f o r   t i m e  s t e p%9d   ( at time%12.5E )\n\n",cycle,time);
  sprintf(dirname,"(%s)",shell->system);
  fprintf(fp," element  materl%-8s\n",dirname);
  fprintf(fp," ipt-shl  stress       sig-xx      sig-yy      sig");
  fprintf(fp,"-zz      sig-xy      sig-yz      sig-zx       plastic\n");
  fprintf(fp,"           state                                  ");
  fprintf(fp,"                                               strain \n");

  for(i=k=0; i<length; i++) {
    fprintf(fp,"%8d-%7d\n",shell->ids[i],shell->mat[i]);
    for(j=0; j<shell->nip[i]; j++,k++) {
      fprintf(fp,"%4d-%3d %-7s ",j+1,shell->iop[i],shell->states[shell->state[k]-1]);
      fprintf(fp,"%12.4E%12.4E%12.4E",shell->sxx[k],shell->syy[k],shell->szz[k]);
      fprintf(fp,"%12.4E%12.4E%12.4E%14.4E\n",shell->sxy[k],shell->syz[k],
                                              shell->szx[k],shell->ps[k]);
    }
  }
  if(have_strain) {
    if(lsda_read(handle,LSDA_FLOAT,"lower_eps_xx",0,length,shell->lxx) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"lower_eps_yy",0,length,shell->lyy) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"lower_eps_zz",0,length,shell->lzz) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"lower_eps_xy",0,length,shell->lxy) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"lower_eps_yz",0,length,shell->lyz) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"lower_eps_zx",0,length,shell->lzx) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"upper_eps_xx",0,length,shell->uxx) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"upper_eps_yy",0,length,shell->uyy) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"upper_eps_zz",0,length,shell->uzz) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"upper_eps_xy",0,length,shell->uxy) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"upper_eps_yz",0,length,shell->uyz) != length) return 0;
    if(lsda_read(handle,LSDA_FLOAT,"upper_eps_zx",0,length,shell->uzx) != length) return 0;

/*
  all the blanks here are silly, but are output by DYNA so.....
*/
    sprintf(dirname,"(%s)",shell->system);
    fprintf(fp,"\n strains %-8s      eps-xx      eps-yy      eps",dirname);
    fprintf(fp,"-zz      eps-xy      eps-yz      eps-zx                                    \n");
    fprintf(fp,"                                                  ");
    fprintf(fp,"                                                                   \n");

    for(i=0; i<length; i++) {
      fprintf(fp,"%8d-%7d\n",shell->ids[i],shell->mat[i]);
      fprintf(fp," lower surface   %12.4E%12.4E%12.4E",shell->lxx[i],shell->lyy[i],shell->lzz[i]);
      fprintf(fp,"%12.4E%12.4E%12.4E\n",shell->lxy[i],shell->lyz[i],shell->lzx[i]);
      fprintf(fp," upper surface   %12.4E%12.4E%12.4E",shell->uxx[i],shell->uyy[i],shell->uzz[i]);
      fprintf(fp,"%12.4E%12.4E%12.4E\n",shell->uxy[i],shell->uyz[i],shell->uzx[i]);
    }
  }
  return 1;
}
/*
  GLSTAT file
*/
translate_glstat(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char types[20][32];
  char title[81];
  char version[11];
  char date[11];
  int cycle;
  float *swe;
  int nsw;
  float x;
  FILE *fp;

  lsda_cd(handle,"/glstat/metadata");
  printf("Extracting GLSTAT data\n");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"element_types",&typeid,&length,&filenum);
  lsda_read(handle,LSDA_I1,"element_types",0,length,dirname);
/*
  parse dirname to split out the element types
*/
  for(i=j=k=0; i<length; i++) {
    if(dirname[i] == ',') {
      types[j][k]=0;
      j++;
      k=0;
    } else {
      types[j][k++]=dirname[i];
    }
  }
  types[j][k]=0;
/*
  see if we have any stonewall energies, and if so allocate space for
  them
*/
  lsda_queryvar(handle,"../d000001/stonewall_energy",&typeid,&length,&filenum);
  if(typeid > 0) {
    nsw = length;
    swe = (float *) malloc(nsw*sizeof(float));
  } else {
    nsw = -1;
  }
/*
  open file and write header
*/
  fp=fopen("glstat","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
/*
  Loop through time states and write each one
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/glstat/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_INT,"cycle",0,1,&cycle) != 1) break;
    if(lsda_read(handle,LSDA_INT,"ts_eltype",0,1,&i) != 1) {
      fprintf(fp,"\n\n dt of cycle%8d is controlled by load curve\n\n",cycle);
    } else {
      if(lsda_read(handle,LSDA_INT,"ts_element",0,1,&j) != 1) break;
      fprintf(fp,"\n\n dt of cycle%8d is controlled by %-11selement%8d\n\n",
        cycle,types[i-1],j);
    }
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&x) != 1) break;
    fprintf(fp," time...........................%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"time_step",0,1,&x) != 1) break;
    fprintf(fp," time step......................%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"kinetic_energy",0,1,&x) != 1) break;
    fprintf(fp," kinetic energy.................%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"internal_energy",0,1,&x) != 1) break;
    fprintf(fp," internal energy................%14.5E\n",x);
    if(nsw > 0) {
      if(lsda_read(handle,LSDA_FLOAT,"stonewall_energy",0,nsw,swe) != nsw) break;
      for(i=0; i<nsw; i++)
        fprintf(fp," stonewall energy...............%14.5E wall#%2d\n",swe[i],i+1);
    }
    if(lsda_read(handle,LSDA_FLOAT,"rb_stopper_energy",0,1,&x) == 1) 
      fprintf(fp," rigid body stopper energy......%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"spring_and_damper_energy",0,1,&x) == 1) 
      fprintf(fp," spring and damper energy.......%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"hourglass_energy",0,1,&x) == 1) 
      fprintf(fp," hourglass energy ..............%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"system_damping_energy",0,1,&x) != 1) break;
    fprintf(fp," system damping energy..........%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"sliding_interface_energy",0,1,&x) != 1) break;
    fprintf(fp," sliding interface energy.......%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"external_work",0,1,&x) != 1) break;
    fprintf(fp," external work..................%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"total_energy",0,1,&x) != 1) break;
    fprintf(fp," total energy...................%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"energy_ratio",0,1,&x) != 1) break;
    fprintf(fp," total energy / initial energy..%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"global_x_velocity",0,1,&x) != 1) break;
    fprintf(fp," global x velocity..............%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"global_y_velocity",0,1,&x) != 1) break;
    fprintf(fp," global y velocity..............%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"global_z_velocity",0,1,&x) != 1) break;
    fprintf(fp," global z velocity..............%14.5E\n",x);
    if(lsda_read(handle,LSDA_INT,"nzc",0,1,&i) != 1) break;
    fprintf(fp," time per zone cycle.(nanosec)..%14d\n",i);
    if(lsda_read(handle,LSDA_INT,"num_bad_shells",0,1,&i) == 1) {
      fprintf(fp,"\n\n number of shell elements that  \n");
      fprintf(fp," reached the minimum time step..%5d\n",i);
    }
    if(lsda_read(handle,LSDA_FLOAT,"added_mass",0,1,&x) == 1)
      fprintf(fp,"\n\n added mass.....................%14.5E\n",x);
    if(lsda_read(handle,LSDA_FLOAT,"percent_increase",0,1,&x) == 1)
      fprintf(fp," percentage increase............%14.5E\n",x);
  }
  fclose(fp);
  if(nsw > 0) free(swe);
  printf("      %d states extracted\n",state-1);
}
/*
  SSSTAT file
*/
translate_ssstat(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char types[20][32];
  char title[81];
  char version[11];
  char date[11];
  int *systems;
  int *ids;
  int cycle;
  float keg, ieg, heg, time, time_step;
  float *ke, *ie, *he, *xm, *ym, *zm, *ker, *ier;
  FILE *fp;

  lsda_cd(handle,"/glstat/metadata");
  printf("Extracting SSSTAT data\n");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"element_types",&typeid,&length,&filenum);
  lsda_read(handle,LSDA_I1,"element_types",0,length,dirname);
/*
  parse dirname to split out the element types
*/
  for(i=j=k=0; i<length; i++) {
    if(dirname[i] == ',') {
      types[j][k]=0;
      j++;
      k=0;
    } else {
      types[j][k++]=dirname[i];
    }
  }
  types[j][k]=0;
/*
  Now data from ssstat
*/
  lsda_cd(handle,"/ssstat/metadata");
  lsda_queryvar(handle,"systems",&typeid,&length,&filenum);
  num = length;

  systems = (int *) malloc(num*sizeof(int));
  ke = (float *) malloc(num*sizeof(float));
  ie = (float *) malloc(num*sizeof(float));
  he = (float *) malloc(num*sizeof(float));
  xm = (float *) malloc(num*sizeof(float));
  ym = (float *) malloc(num*sizeof(float));
  zm = (float *) malloc(num*sizeof(float));
  ker = (float *) malloc(num*sizeof(float));
  ier = (float *) malloc(num*sizeof(float));

  lsda_read(handle,LSDA_INT,"systems",0,num,systems);
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  ids = (int *) malloc(length*sizeof(int));
  lsda_read(handle,LSDA_INT,"ids",0,length,ids);
/*
  open file and write header
*/
  fp=fopen("ssstat","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
/*
  susbsystem info
*/
  for(i=j=0; i<num; i++) {
    fprintf(fp,"\n\n subsystem definition ID=%5d part ID list:\n",i+1);
    for(k=0; k<systems[i]; k++) {
      fprintf(fp,"%10d",ids[j++]);
      if((k+1)%8 == 0) fprintf(fp,"\n");
    }
    if(k%8 != 0) fprintf(fp,"\n");
  }
  free(ids);
/*
  Loop through time states and write each one.  First get the necessary
  global data from the glstat directory
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/glstat/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_INT,"cycle",0,1,&cycle) != 1) break;
    if(lsda_read(handle,LSDA_INT,"ts_eltype",0,1,&i) != 1) {
      fprintf(fp,"\n\n dt of cycle%8d is controlled by load curve\n\n",cycle);
    } else {
      if(lsda_read(handle,LSDA_INT,"ts_element",0,1,&j) != 1) break;
      fprintf(fp,"\n\n dt of cycle%8d is controlled by %-11selement%8d\n\n",
        cycle,types[i-1],j);
    }
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"time_step",0,1,&time_step) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"kinetic_energy",0,1,&keg) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"internal_energy",0,1,&ieg) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"hourglass_energy",0,1,&heg) != 1) heg = 0.;
/*
  Now get the subsystem data
*/
    sprintf(dirname,"/ssstat/d%6.6d",state);
    lsda_cd(handle,dirname);

    if(lsda_read(handle,LSDA_FLOAT,"kinetic_energy",0,num,ke) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"internal_energy",0,num,ie) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"hourglass_energy",0,num,he) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_momentum",0,num,xm) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_momentum",0,num,ym) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_momentum",0,num,zm) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"kinetic_energy_ratios",0,num,ker) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"internal_energy_ratios",0,num,ier) != num) break;
    fprintf(fp," time........................   %14.5E\n",time);
    fprintf(fp," time step...................   %14.5E\n",time_step);
    fprintf(fp," kinetic energy global.......   %14.5E\n",keg);
    fprintf(fp," kinetic energy subsystems ..");
    for(i=0; i<num; i++) {
      if(i>0 && i%3 == 0) fprintf(fp,"                             ");
      fprintf(fp,"%3d.%13.5E",i+1,ke[i]);
      if((i+1)%3 == 0) fprintf(fp,"\n");
    }
    if(num%3 != 0) fprintf(fp,"\n");
    fprintf(fp," internal energy global......   %14.5E\n",ieg);
    fprintf(fp," internal energy subsystems .");
    for(i=0; i<num; i++) {
      if(i>0 && i%3 == 0) fprintf(fp,"                             ");
      fprintf(fp,"%3d.%13.5E",i+1,ie[i]);
      if((i+1)%3 == 0) fprintf(fp,"\n");
    }
    if(num%3 != 0) fprintf(fp,"\n");
    fprintf(fp," hourglass energy global ....   %14.5E\n",heg);
    fprintf(fp," hourglass energy subsystems ");
    for(i=0; i<num; i++) {
      if(i>0 && i%3 == 0) fprintf(fp,"                             ");
      fprintf(fp,"%3d.%13.5E",i+1,he[i]);
      if((i+1)%3 == 0) fprintf(fp,"\n");
    }
    if(num%3 != 0) fprintf(fp,"\n");
    fprintf(fp," kinetic energy ratios ......");
    for(i=0; i<num; i++) {
      if(i>0 && i%3 == 0) fprintf(fp,"                             ");
      fprintf(fp,"%3d.%13.5E",i+1,ker[i]);
      if((i+1)%3 == 0) fprintf(fp,"\n");
    }
    if(num%3 != 0) fprintf(fp,"\n");
    fprintf(fp," internal energy ratios .....");
    for(i=0; i<num; i++) {
      if(i>0 && i%3 == 0) fprintf(fp,"                             ");
      fprintf(fp,"%3d.%13.5E",i+1,ier[i]);
      if((i+1)%3 == 0) fprintf(fp,"\n");
    }
    if(num%3 != 0) fprintf(fp,"\n");
    fprintf(fp," x-momentum subsystems ......");
    for(i=0; i<num; i++) {
      if(i>0 && i%3 == 0) fprintf(fp,"                             ");
      fprintf(fp,"%3d.%13.5E",i+1,xm[i]);
      if((i+1)%3 == 0) fprintf(fp,"\n");
    }
    if(num%3 != 0) fprintf(fp,"\n");
    fprintf(fp," y-momentum subsystems ......");
    for(i=0; i<num; i++) {
      if(i>0 && i%3 == 0) fprintf(fp,"                             ");
      fprintf(fp,"%3d.%13.5E",i+1,ym[i]);
      if((i+1)%3 == 0) fprintf(fp,"\n");
    }
    if(num%3 != 0) fprintf(fp,"\n");
    fprintf(fp," z-momentum subsystems ......");
    for(i=0; i<num; i++) {
      if(i>0 && i%3 == 0) fprintf(fp,"                             ");
      fprintf(fp,"%3d.%13.5E",i+1,zm[i]);
      if((i+1)%3 == 0) fprintf(fp,"\n");
    }
    if(num%3 != 0) fprintf(fp,"\n");
  }
  fclose(fp);
  free(ier);
  free(ker);
  free(zm);
  free(ym);
  free(xm);
  free(he);
  free(ie);
  free(ke);
  free(systems);
  printf("      %d states extracted\n",state-1);
}
/*
  DEFORC file
*/
translate_deforc(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  int have_mass, have_he;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *ids, *irot;
  float *fx,*fy,*fz,*rf,*disp;
  float time;
  FILE *fp;

  printf("Extracting DEFORC data\n");
  lsda_cd(handle,"/deforc/metadata");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num = length;

  ids  = (int *) malloc(num*sizeof(int));
  irot = (int *) malloc(num*sizeof(int));
  fx  = (float *) malloc(num*sizeof(float));
  fy  = (float *) malloc(num*sizeof(float));
  fz  = (float *) malloc(num*sizeof(float));
  rf  = (float *) malloc(num*sizeof(float));
  disp = (float *) malloc(num*sizeof(float));
  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
  lsda_read(handle,LSDA_INT,"irot",0,num,irot);
/*
  open file and write header
*/
  fp=fopen("deforc","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/deforc/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_force",0,num,fx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_force",0,num,fy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_force",0,num,fz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"resultant_force",0,num,rf) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"displacement",0,num,disp) != num) break;

    fprintf(fp,"\n time.........................%14.5E\n",time);
    for(i=0; i<num; i++) {
      fprintf(fp," spring/damper number.........%10d\n",ids[i]);
      if(irot[i] == 0) {
        fprintf(fp," x-force......................%14.5E\n",fx[i]);
        fprintf(fp," y-force......................%14.5E\n",fy[i]);
        fprintf(fp," z-force......................%14.5E\n",fz[i]);
        fprintf(fp," resultant force..............%14.5E\n",rf[i]);
        fprintf(fp," change in length.............%14.5E\n",disp[i]);
      } else {
        fprintf(fp," x-moment.....................%14.5E\n",fx[i]);
        fprintf(fp," y-moment.....................%14.5E\n",fy[i]);
        fprintf(fp," z-moment.....................%14.5E\n",fz[i]);
        fprintf(fp," resultant moment.............%14.5E\n",rf[i]);
        fprintf(fp," relative rotation............%14.5E\n",disp[i]);
      }
    }
  }
  fclose(fp);
  free(disp);
  free(rf);
  free(fz);
  free(fy);
  free(fx);
  free(irot);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  MATSUM file
*/
translate_matsum(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  int have_mass, have_he;
  LSDA_Length length;
  char dirname[256];
  char types[20][32];
  char title[81];
  char version[11];
  char date[11];
  int *ids;
  int cycle;
  float *ke, *ie, *he, *mass, *xm, *ym, *zm, *xrbv, *yrbv, *zrbv;
  float mm,time;
  int mid;
  FILE *fp;

  lsda_cd(handle,"/matsum/metadata");
  printf("Extracting MATSUM data\n");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num = length;

  ids = (int *) malloc(num*sizeof(int));
  ie = (float *) malloc(num*sizeof(float));
  ke = (float *) malloc(num*sizeof(float));
  mass = (float *) malloc(num*sizeof(float));
  xm = (float *) malloc(num*sizeof(float));
  ym = (float *) malloc(num*sizeof(float));
  zm = (float *) malloc(num*sizeof(float));
  xrbv = (float *) malloc(num*sizeof(float));
  yrbv = (float *) malloc(num*sizeof(float));
  zrbv = (float *) malloc(num*sizeof(float));
  he = (float *) malloc(num*sizeof(float));
  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
/*
  open file and write header
*/
  fp=fopen("matsum","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  output_legend(handle,fp,1,1);
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/matsum/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"internal_energy",0,num,ie) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"kinetic_energy",0,num,ke) != num) break;
    lsda_queryvar(handle,"mass",&have_mass,&length,&filenum);
    if(have_mass > 0)
      if(lsda_read(handle,LSDA_FLOAT,"mass",0,num,mass) != num) break;
    lsda_queryvar(handle,"hourglass_energy",&have_he,&length,&filenum);
    if(have_he > 0)
      if(lsda_read(handle,LSDA_FLOAT,"hourglass_energy",0,num,he) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_momentum",0,num,xm) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_momentum",0,num,ym) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_momentum",0,num,zm) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_rbvelocity",0,num,xrbv) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_rbvelocity",0,num,yrbv) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_rbvelocity",0,num,zrbv) != num) break;

    fprintf(fp,"\n\n time =%13.4E\n",time);
    for(i=0; i<num; i++) {
      if(ids[i] < 100000 )
        fprintf(fp," mat.#=%5d   ",ids[i]);
      else
        fprintf(fp," mat.#=%8d",ids[i]);
      fprintf(fp,"          inten=%13.4E     kinen=%13.4E\n",ie[i],ke[i]);
      fprintf(fp," x-mom=%13.4E     y-mom=%13.4E     z-mom=%13.4E\n",
         xm[i],ym[i],zm[i]);
      fprintf(fp," x-rbv=%13.4E     y-rbv=%13.4E     z-rbv=%13.4E\n",
         xrbv[i],yrbv[i],zrbv[i]);
      if(have_he>0) {
        fprintf(fp,"                         hgeng=%13.4E     ",he[i]);
        if(have_mass>0)
          fprintf(fp,"+mass=%13.4E\n",mass[i]);
        else
          fprintf(fp,"\n");
      } else if(have_mass>0) {
          fprintf(fp,"                                                 ");
          fprintf(fp,"+mass=%13.4E\n",mass[i]);
      }
    }
    lsda_queryvar(handle,"brick_id",&typeid,&length,&filenum);
    if(typeid > 0) {
      lsda_read(handle,LSDA_FLOAT,"max_brick_mass",0,1,&mm);
      lsda_read(handle,LSDA_INT,"brick_id",0,1,&mid);
      fprintf(fp,"\n\n       Maximum mass increase in brick elements      =");
      fprintf(fp,"%13.4E ID=%8d\n",mm,mid);
    }
    lsda_queryvar(handle,"beam_id",&typeid,&length,&filenum);
    if(typeid > 0) {
      lsda_read(handle,LSDA_FLOAT,"max_beam_mass",0,1,&mm);
      lsda_read(handle,LSDA_INT,"beam_id",0,1,&mid);
      fprintf(fp,"\n\n       Maximum mass increase in beam elements       =");
      fprintf(fp,"%13.4E ID=%8d\n",mm,mid);
    }
    lsda_queryvar(handle,"shell_id",&typeid,&length,&filenum);
    if(typeid > 0) {
      lsda_read(handle,LSDA_FLOAT,"max_shell_mass",0,1,&mm);
      lsda_read(handle,LSDA_INT,"shell_id",0,1,&mid);
      fprintf(fp,"\n\n       Maximum mass increase in shell elements      =");
      fprintf(fp,"%13.4E ID=%8d\n",mm,mid);
    }
    lsda_queryvar(handle,"thick_shell_id",&typeid,&length,&filenum);
    if(typeid > 0) {
      lsda_read(handle,LSDA_FLOAT,"max_thick_shell_mass",0,1,&mm);
      lsda_read(handle,LSDA_INT,"thick_shell_id",0,1,&mid);
      fprintf(fp,"\n\n       Maximum mass increase in thick shell elements=");
      fprintf(fp,"%13.4E ID=%8d\n",mm,mid);
    }
  }
  fclose(fp);
  free(he);
  free(zrbv);
  free(yrbv);
  free(xrbv);
  free(zm);
  free(ym);
  free(xm);
  free(mass);
  free(ke);
  free(ie);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  NCFORC file
*/
typedef struct {
  int master;      /* 0 for slave, 1 for master */
  int inum;        /* interface number for output */
  int *ids;        /* user ids for nodes */
  int n;           /* number of nodes */
  char legend[70];
  char dname[32];  /* so I don't have to keep rebuilding it...*/
} NCFDATA;

int comp_ncn(const void *v1, const void *v2) 
{
  NCFDATA *p1 = (NCFDATA *) v1;
  NCFDATA *p2 = (NCFDATA *) v2;
  if(p1->inum != p2->inum) return (p1->inum - p2->inum);
  return (p1->master - p2->master);
}

translate_ncforc(int handle)
{
/*
  This one is a bit strange in that there are separate dirs
  for each slave/master side of each interface.  The only
  way to tell how many there are is to count the dirs.
  Fortunately, they appear in the same order we want to
  output them in.....
  NOT!  readdir now returns things in alphabetic order, so we will
  have to resort them according to their number.....
*/
  NCFDATA *dp;
  int ndirs;
  LSDADir *ldp;
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  float *xf,*yf,*zf,*p, *x, *y, *z;
  float time;
  FILE *fp;
  int have_legend=0;

  printf("Extracting NCFORC data\n");

  ldp = lsda_opendir(handle,"/ncforc");
  for(ndirs=0; ;ndirs++) {
    lsda_readdir(ldp,dirname,&typeid,&length,&filenum);
    if(dirname[0]==0)  break ;   /* end of listing */
  }
  lsda_closedir(ldp);

  dp = (NCFDATA *) malloc(ndirs * sizeof(NCFDATA));

  ldp = lsda_opendir(handle,"/ncforc");
  for(i=0;i<ndirs ;i++) {
    lsda_readdir(ldp,dirname,&typeid,&length,&filenum);
    if(strcmp(dirname,"metadata")==0) {  /* skip this one */
      i--;
      continue;
    }
    dp[i].master = (dirname[0] == 'm');
    if(dp[i].master)
      sscanf(dirname+7,"%d",&dp[i].inum);
    else
      sscanf(dirname+6,"%d",&dp[i].inum);
    sprintf(dp[i].dname,"/ncforc/%s",dirname);
  }
  lsda_closedir(ldp);
  qsort(dp,ndirs,sizeof(NCFDATA),comp_ncn);
/*
  Ok, now go through each directory and get the list of user ids.
  Also, build up legend info if we have any
*/
  for(i=j=0; i<ndirs; i++) {
    sprintf(dirname,"%s/metadata",dp[i].dname);
    lsda_cd(handle,dirname);
    lsda_read(handle,LSDA_I1,"title",0,80,title);
    lsda_read(handle,LSDA_I1,"version",0,10,version);
    lsda_read(handle,LSDA_I1,"date",0,10,date);
    title[72]=0;
    version[10]=0;
    date[10]=0;
    lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
    dp[i].n = length;
    if(j < length) j = length;
    dp[i].ids = (int *) malloc(dp[i].n*sizeof(int));
    lsda_read(handle,LSDA_INT,"ids",0,length,dp[i].ids);
    lsda_queryvar(handle,"legend",&typeid,&length,&filenum);
    if(typeid > 0) {
      lsda_read(handle,LSDA_I1,"legend",0,70,dp[i].legend);
      have_legend=1;
    } else
      dp[i].legend[0]=0;
  }
  xf = (float *) malloc(j*sizeof(float));
  yf = (float *) malloc(j*sizeof(float));
  zf = (float *) malloc(j*sizeof(float));
  p  = (float *) malloc(j*sizeof(float));
  x  = (float *) malloc(j*sizeof(float));
  y  = (float *) malloc(j*sizeof(float));
  z  = (float *) malloc(j*sizeof(float));
/*
  open file and write header
*/
  fp=fopen("ncforc","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  if(have_legend) {
    fprintf(fp,"\n{BEGIN LEGEND\n");
    fprintf(fp," Entity #        Title\n");
    for(i=j=0; i<ndirs; i++) {
      if(dp[i].legend[0] && dp[i].inum != j) {
        fprintf(fp,"%9d     %.70s\n",dp[i].inum,dp[i].legend);
        j=dp[i].inum;
      }
    }
    fprintf(fp,"{END LEGEND}\n\n");
  }
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    for(k=0; k<ndirs; k++) {
      sprintf(dirname,"%s/d%6.6d",dp[k].dname,state);
      lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
      if(typeid != 0) goto done;
      lsda_cd(handle,dirname);
      if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) goto done;
      if(lsda_read(handle,LSDA_FLOAT,"x_force",0,dp[k].n,xf) != dp[k].n) goto done;
      if(lsda_read(handle,LSDA_FLOAT,"y_force",0,dp[k].n,yf) != dp[k].n) goto done;
      if(lsda_read(handle,LSDA_FLOAT,"z_force",0,dp[k].n,zf) != dp[k].n) goto done;
      if(lsda_read(handle,LSDA_FLOAT,"pressure",0,dp[k].n,p) != dp[k].n) goto done;
      if(lsda_read(handle,LSDA_FLOAT,"x",0,dp[k].n,x) != dp[k].n) goto done;
      if(lsda_read(handle,LSDA_FLOAT,"y",0,dp[k].n,y) != dp[k].n) goto done;
      if(lsda_read(handle,LSDA_FLOAT,"z",0,dp[k].n,z) != dp[k].n) goto done;

      fprintf(fp,"\n\n\n forces (t=%11.5E) for interface%10d %s side\n\n",
        time,dp[k].inum,(dp[k].master ? "master" : "slave "));
      fprintf(fp,"     node           x-force/      y-force/      z-force/");
      fprintf(fp,"     pressure/\n");
      fprintf(fp,"                   coordinate    coordinate    coordinate\n");
      for(i=0; i<dp[k].n; i++) {
        fprintf(fp,"%10d      %14.5E%14.5E%14.5E%14.5E\n",dp[k].ids[i],
          xf[i],yf[i],zf[i],p[i]);
        fprintf(fp,"                %14.5E%14.5E%14.5E\n",x[i],y[i],z[i]);
      }
    }
  }
done:
  fclose(fp);
  free(z);
  free(y);
  free(x);
  free(p);
  free(zf);
  free(yf);
  free(xf);
  for(i=0; i<ndirs; i++)
    free(dp[i].ids);
  free(dp);
  printf("      %d states extracted\n",state-1);
}
/*
  RCFORC file
*/
translate_rcforc(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *ids;
  int *sides;
  float *xf,*yf,*zf,*mass;
  float time;
  FILE *fp;

  lsda_cd(handle,"/rcforc/metadata");
  printf("Extracting RCFORC data\n");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num = length;

  ids = (int *) malloc(num*sizeof(int));
  sides = (int *) malloc(num*sizeof(int));
  xf = (float *) malloc(num*sizeof(float));
  yf = (float *) malloc(num*sizeof(float));
  zf = (float *) malloc(num*sizeof(float));
  mass = (float *) malloc(num*sizeof(float));
  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
  lsda_read(handle,LSDA_INT,"side",0,num,sides);
/*
  open file and write header
*/
  fp=fopen("rcforc","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  output_legend(handle,fp,1,1);
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/rcforc/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_force",0,num,xf) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_force",0,num,yf) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_force",0,num,zf) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"mass",0,num,mass) != num) break;

    for(i=0; i<num; i++) {
      if(sides[i])
        fprintf(fp,"  master%11d time",ids[i]);
      else
        fprintf(fp,"  slave %11d time",ids[i]);
/*
      fprintf(fp,"%14.6Ex %14.7Ey %14.7Ez %14.7Emass %12.5E\n",
*/
      fprintf(fp,"%12.5E  x %12.5E  y %12.5E  z %12.5E mass %12.5E\n",
        time,xf[i],yf[i],zf[i],mass[i]);
    }
  }
  fclose(fp);
  free(mass);
  free(zf);
  free(yf);
  free(xf);
  free(sides);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  SPCFORC file
*/
translate_spcforc(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length,length2;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *tids,*rids,numt,numr;
  float *xf,*yf,*zf,*xm,*ym,*zm,xtot,ytot,ztot;
  float time;
  FILE *fp;

  lsda_cd(handle,"/spcforc/metadata");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"force_ids",&typeid,&length,&filenum);
  if(typeid > 0) {
    numt = length;
    tids = (int *) malloc(numt*sizeof(int));
    xf   = (float *) malloc(numt*sizeof(float));
    yf   = (float *) malloc(numt*sizeof(float));
    zf   = (float *) malloc(numt*sizeof(float));
    lsda_read(handle,LSDA_INT,"force_ids",0,length,tids);
  } else {
    numt = 0;
  }
  lsda_queryvar(handle,"moment_ids",&typeid,&length,&filenum);
  if(typeid > 0) {
    numr = length;
    rids = (int *) malloc(numr*sizeof(int));
    xm   = (float *) malloc(numr*sizeof(float));
    ym   = (float *) malloc(numr*sizeof(float));
    zm   = (float *) malloc(numr*sizeof(float));
    lsda_read(handle,LSDA_INT,"moment_ids",0,length,rids);
  } else {
    numr = 0;
  }
  if(numt == 0 && numr == 0) return;
/*
  open file and write header
*/
  printf("Extracting SPCFORC data\n");
  fp=fopen("spcforc","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  fprintf(fp," single point constraint forces\n\n");
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/spcforc/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",        0,  1,&time) != 1) break;
    if(numt) {
      if(lsda_read(handle,LSDA_FLOAT,"x_force",0,numt,xf) != numt) break;
      if(lsda_read(handle,LSDA_FLOAT,"y_force",0,numt,yf) != numt) break;
      if(lsda_read(handle,LSDA_FLOAT,"z_force",0,numt,zf) != numt) break;
    }
    if(numr) {
      if(lsda_read(handle,LSDA_FLOAT,"x_moment",0,numr,xm) != numr) break;
      if(lsda_read(handle,LSDA_FLOAT,"y_moment",0,numr,ym) != numr) break;
      if(lsda_read(handle,LSDA_FLOAT,"z_moment",0,numr,zm) != numr) break;
    }
    if(lsda_read(handle,LSDA_FLOAT,"x_resultant",0,1,&xtot) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_resultant",0,1,&ytot) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_resultant",0,1,&ztot) != 1) break;
/*
  Now, it appears that the serial code normally outputs them in increasing
  node order, with translations before moments if both appear.  So we will
  put them out that way also for compatibility
*/
    fprintf(fp," output at time =%14.5E\n",time);
    i=j=0;
    while(i<numt || j<numr) {
      if(i < numt) {
        if(j >= numr || tids[i] <= rids[j]) {
          fprintf(fp," node=%8d local x,y,z forces =%14.4E%14.4E%14.4E\n",
           tids[i],xf[i],yf[i],zf[i]);
          i++;
        }
      }
      if(j < numr) {
        if(i >= numt || tids[i] > rids[j]) {
          fprintf(fp," node=%8d local x,y,z moments=%14.4E%14.4E%14.4E\n",
           rids[j],xm[j],ym[j],zm[j]);
          j++;
        }
      }
    }
    fprintf(fp,"             force resultants   =%14.4E%14.4E%14.4E\n",xtot,ytot,ztot);
  }
  fclose(fp);
  if(numr) {
    free(zm);
    free(ym);
    free(xm);
    free(rids);
  }
  if(numt) {
    free(zf);
    free(yf);
    free(xf);
    free(tids);
  }
  printf("      %d states extracted\n",state-1);
}
/*
  SWFORC file
*/
translate_swforc(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length,length2;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *fflag,*ids,*type,nnnodal;
  float *axial,*shear,*ftime,*emom,*swlen;
  float time;
  FILE *fp;

  lsda_cd(handle,"/swforc/metadata");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num = length;
  ids = (int *) malloc(num*sizeof(int));
  type = (int *) malloc(num*sizeof(int));
  fflag = (int *) malloc(num*sizeof(int));
  axial = (float *) malloc(num*sizeof(float));
  shear = (float *) malloc(num*sizeof(float));
  ftime = (float *) malloc(num*sizeof(float));
  swlen = (float *) malloc(num*sizeof(float));
  lsda_queryvar(handle,"emom",&typeid,&length2,&filenum);
  if(typeid > 0) {
    nnnodal = length2;
    emom = (float *) malloc(nnnodal*sizeof(float));
  } else {
    nnnodal = 0;
  }
  lsda_read(handle,LSDA_INT,"ids",0,length,ids);
  lsda_read(handle,LSDA_INT,"types",0,length,type);
/*
  open file and write header
*/
  printf("Extracting SWFORC data\n");
  fp=fopen("swforc","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/swforc/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",        0,  1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"axial",       0,num,axial) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"shear",       0,num,shear) != num) break;
    if(lsda_read(handle,LSDA_INT  ,"failure_flag",0,num,fflag) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"failure_time",0,num,ftime) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"length",0,num,swlen) != num) {
      memset(swlen,0,num*sizeof(float));
    }
    if(nnnodal)
      if(lsda_read(handle,LSDA_FLOAT,"emom",0,nnnodal,emom) != nnnodal) break;

    fprintf(fp,"\n constraint #      axial        shear         time");
    fprintf(fp,"                                                length\n");
    for(i=j=0; i<num; i++) {
      fprintf(fp,"      %5d%13.5E%13.5E%13.5E  %-7s    ",
       i+1,axial[i],shear[i],time,(fflag[i] ? "failure" : "       "));
      if(type[i] == 0)
        fprintf(fp,"constraint/weld  ID %8d\n",ids[i]);
      else if(type[i] == 1)
        fprintf(fp,"generalized weld ID %8d\n",ids[i]);
      else if(type[i] == 2) {
        fprintf(fp,"spotweld beam  ID   %8d",ids[i]);
        if(fflag[i])
          fprintf(fp,"  failure time=%12.4E\n",ftime[i]);
        else
          fprintf(fp,"%13.5E\n",swlen[i]);
      } else if(type[i] == 3) {
        fprintf(fp,"spotweld solid ID   %8d",ids[i]);
        if(fflag[i])
          fprintf(fp,"  failure time=%12.4E\n",ftime[i]);
        else
          fprintf(fp,"%13.5E\n",swlen[i]);
      } else if(type[i] == 4) {
        fprintf(fp,"nonnodal cnst  ID   %8d",ids[i]);
        if(fflag[i])
          fprintf(fp,"  failure time=%12.4E  %13.5E\n",ftime[i],emom[j]);
        else
          fprintf(fp,"                             %13.5E\n",emom[j]);
        j++;
      }
    }
  }
  fclose(fp);
  if(nnnodal) free(emom);
  free(swlen);
  free(ftime);
  free(shear);
  free(axial);
  free(fflag);
  free(type);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  ABSTAT file
*/
translate_abstat(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *ids;
  float *v,*p,*ie,*din,*den,*dout,*tm,*gt,*sa,*r;
  float time;
  FILE *fp;

  lsda_cd(handle,"/abstat/metadata");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"../d000001/volume",&typeid,&length,&filenum);
  if(typeid < 0) return;
  num = length;

  ids  = (int *) malloc(num*sizeof(int));
  if(lsda_read(handle,LSDA_INT,"ids",0,num,ids) != num) {
    for(i=0; i<num; i++)
       ids[i] = i+1;
  }
  v    = (float *) malloc(num*sizeof(float));
  p    = (float *) malloc(num*sizeof(float));
  ie   = (float *) malloc(num*sizeof(float));
  din  = (float *) malloc(num*sizeof(float));
  den  = (float *) malloc(num*sizeof(float));
  dout = (float *) malloc(num*sizeof(float));
  tm   = (float *) malloc(num*sizeof(float));
  gt   = (float *) malloc(num*sizeof(float));
  sa   = (float *) malloc(num*sizeof(float));
  r    = (float *) malloc(num*sizeof(float));
/*
  open file and write header
*/
  printf("Extracting ABSTAT data\n");
  fp=fopen("abstat","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  output_legend(handle,fp,1,1);
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/abstat/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",           0,  1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"volume",         0,num,    v) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"pressure",       0,num,    p) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"internal_energy",0,num,   ie) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dm_dt_in",       0,num,  din) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"density",        0,num,  den) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dm_dt_out",      0,num, dout) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"total_mass",     0,num,   tm) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"gas_temp",       0,num,   gt) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"surface_area",   0,num,   sa) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"reaction",       0,num,    r) != num) break;
    fprintf(fp,"\n\n      time   airbag/cv #  volume        pressure    internal energy");
    fprintf(fp,"      dm/dt in      density dm/dt out  total mass gas temp. surface area");
    fprintf(fp,"   reaction\n");
    for(i=0; i<num; i++) {
      fprintf(fp,"%12.5E%8d%15.4E%15.4E%15.4E%15.4E%15.4E",
       time,ids[i],v[i],p[i],ie[i],din[i],den[i]);
      fprintf(fp,"%11.3E%11.3E%11.3E%11.3E%11.3E\n",
       dout[i],tm[i],gt[i],sa[i],r[i]);
    }

  }
  fclose(fp);
  free(r);
  free(sa);
  free(gt);
  free(tm);
  free(dout);
  free(den);
  free(din);
  free(ie);
  free(p);
  free(v);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  NODFOR file
*/
translate_nodfor(int handle)
{
  int i,j,k,n,typeid,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *ids, *groups, *local;
  int nnodes, ngroups, nlocal;
  float *xf,*yf,*zf,*e,*xt,*yt,*zt,*et,*xl,*yl,*zl;
  float time;
  FILE *fp;

  lsda_cd(handle,"/nodfor/metadata");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  if(typeid < 0) return;
  nnodes = length;
  lsda_queryvar(handle,"groups",&typeid,&length,&filenum);
  ngroups = length;

  ids   = (int *) malloc(nnodes*sizeof(int));
  local = (int *) malloc(nnodes*sizeof(int));
  groups= (int *) malloc(ngroups*sizeof(int));
  xf    = (float *) malloc(nnodes*sizeof(float));
  yf    = (float *) malloc(nnodes*sizeof(float));
  zf    = (float *) malloc(nnodes*sizeof(float));
  e     = (float *) malloc(nnodes*sizeof(float));
  xt    = (float *) malloc(nnodes*sizeof(float));
  yt    = (float *) malloc(nnodes*sizeof(float));
  zt    = (float *) malloc(nnodes*sizeof(float));
  et    = (float *) malloc(nnodes*sizeof(float));
  lsda_read(handle,LSDA_INT,"ids",0,nnodes,ids);
  lsda_read(handle,LSDA_INT,"local",0,ngroups,local);
  lsda_read(handle,LSDA_INT,"groups",0,ngroups,groups);
  for(i=nlocal=0; i<ngroups; i++)
    nlocal += local[i];
  if(nlocal > 0) {
    xl = (float *) malloc(nlocal*sizeof(float));
    yl = (float *) malloc(nlocal*sizeof(float));
    zl = (float *) malloc(nlocal*sizeof(float));
  }
/*
  open file and write header
*/
  printf("Extracting NODFOR data\n");
  fp=fopen("nodfor","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/nodfor/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",  0,   1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"xforce" ,0, nnodes,xf) !=  nnodes &&
       lsda_read(handle,LSDA_FLOAT,"x_force",0, nnodes,xf) !=  nnodes) break;
    if(lsda_read(handle,LSDA_FLOAT,"yforce" ,0, nnodes,yf) !=  nnodes &&
       lsda_read(handle,LSDA_FLOAT,"y_force",0, nnodes,yf) !=  nnodes) break;
    if(lsda_read(handle,LSDA_FLOAT,"zforce" ,0, nnodes,zf) !=  nnodes &&
       lsda_read(handle,LSDA_FLOAT,"z_force",0, nnodes,zf) !=  nnodes) break;
    if(lsda_read(handle,LSDA_FLOAT,"energy",0, nnodes, e) !=  nnodes) break;
    if(lsda_read(handle,LSDA_FLOAT,"xtotal" ,0, ngroups,xt) !=  ngroups &&
       lsda_read(handle,LSDA_FLOAT,"x_total",0, ngroups,xt) !=  ngroups) break;
    if(lsda_read(handle,LSDA_FLOAT,"ytotal" ,0, ngroups,yt) !=  ngroups &&
       lsda_read(handle,LSDA_FLOAT,"y_total",0, ngroups,yt) !=  ngroups) break;
    if(lsda_read(handle,LSDA_FLOAT,"ztotal" ,0, ngroups,zt) !=  ngroups &&
       lsda_read(handle,LSDA_FLOAT,"z_total",0, ngroups,zt) !=  ngroups) break;
    if(lsda_read(handle,LSDA_FLOAT,"etotal",0,ngroups,et) != ngroups) break;
    if(nlocal > 0) {
      if(lsda_read(handle,LSDA_FLOAT,"xlocal" ,0,nlocal,xl) != nlocal &&
         lsda_read(handle,LSDA_FLOAT,"x_local",0,nlocal,xl) != nlocal) break;
      if(lsda_read(handle,LSDA_FLOAT,"ylocal" ,0,nlocal,yl) != nlocal &&
         lsda_read(handle,LSDA_FLOAT,"y_local",0,nlocal,yl) != nlocal) break;
      if(lsda_read(handle,LSDA_FLOAT,"zlocal" ,0,nlocal,zl) != nlocal &&
         lsda_read(handle,LSDA_FLOAT,"z_local",0,nlocal,zl) != nlocal) break;
    }
    fprintf(fp,"\n\n\n\n\n n o d a l   f o r c e   g r o u p");
    fprintf(fp,"    o u t p u t   t=%9.3E\n",time);
    for(i=j=k=0; i<ngroups; i++) {
      fprintf(fp,"\n\n\n\n\n nodal group output number %2d\n\n",i+1);
      for(n=0; n<groups[i]; n++,j++) {
        fprintf(fp," nd#%8d  xforce=%13.4E   yforce=%13.4E  zforce=%13.4E   energy=%13.4E\n",
         ids[j],xf[j],yf[j],zf[j],e[j]);
      }
      fprintf(fp,"              xtotal=%13.4E   ytotal=%13.4E  ztotal=%13.4E   etotal=%13.4E\n",
         xt[i],yt[i],zt[i],et[i]);
      if(local[i] > 0) {
        fprintf(fp,"              xlocal=%13.4E   ylocal=%13.4E  zlocal=%13.4E\n",
         xl[k],yl[k],zl[k]);
        k++;
      }
    }
  }
  fclose(fp);
  if(nlocal > 0) {
    free(zl);
    free(yl);
    free(xl);
  }
  free(et);
  free(zt);
  free(yt);
  free(xt);
  free(e);
  free(zf);
  free(yf);
  free(xf);
  free(groups);
  free(local);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  BNDOUT file
*/
typedef struct {
  char title[84];
  char version[12];
  char date[12];
  int num;
  int *ids;
  float *xf,*yf,*zf,*e,*xm,*ym,*zm;
} BND_DATA;

translate_bndout(int handle)
{
  int i,k,header,typeid,filenum,state;
  LSDA_Length length;
  char dirname[256];
  int have_dn,have_dr,have_p,have_vn,have_vr;
  FILE *fp;
  BND_DATA dn,dr,p,vn,vr;
  float xt,yt,zt,et;
  char *title=NULL, *version, *date;

  lsda_queryvar(handle,"/bndout/discrete/nodes",&typeid,&length,&filenum);
  have_dn= (typeid >= 0);
  lsda_queryvar(handle,"/bndout/discrete/rigidbodies",&typeid,&length,&filenum);
  have_dr= (typeid >= 0);
  lsda_queryvar(handle,"/bndout/pressure",&typeid,&length,&filenum);
  have_p= (typeid >= 0);
  lsda_queryvar(handle,"/bndout/velocity/nodes",&typeid,&length,&filenum);
  have_vn= (typeid >= 0);
  lsda_queryvar(handle,"/bndout/velocity/rigidbodies",&typeid,&length,&filenum);
  have_vr= (typeid >= 0);
/*
  Read metadata
*/
  if(have_dn) {
    lsda_cd(handle,"/bndout/discrete/nodes/metadata");
    lsda_read(handle,LSDA_I1,"title",0,80,dn.title);
    dn.title[72]=0;
    lsda_read(handle,LSDA_I1,"version",0,10,dn.version);
    dn.version[10]=0;
    lsda_read(handle,LSDA_I1,"date",0,10,dn.date);
    dn.date[10]=0;
    lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
    dn.num = length;
    dn.ids = (int *) malloc(dn.num*sizeof(int));
    dn.xf = (float *) malloc(4*dn.num*sizeof(float));
    dn.yf = dn.xf + dn.num;
    dn.zf = dn.yf + dn.num;
    dn.e  = dn.zf + dn.num;
    title = dn.title;
    version = dn.version;
    date = dn.date;
    lsda_read(handle,LSDA_INT,"ids",0,dn.num,dn.ids);
  }
  if(have_dr) {
    lsda_cd(handle,"/bndout/discrete/rigidbodies/metadata");
    lsda_read(handle,LSDA_I1,"title",0,80,dr.title);
    dr.title[72]=0;
    lsda_read(handle,LSDA_I1,"version",0,10,dr.version);
    dr.version[10]=0;
    lsda_read(handle,LSDA_I1,"date",0,10,dr.date);
    dr.date[10]=0;
    lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
    dr.num = length;
    dr.ids = (int *) malloc(dr.num*sizeof(int));
    dr.xf = (float *) malloc(4*dr.num*sizeof(float));
    dr.yf = dr.xf + dr.num;
    dr.zf = dr.yf + dr.num;
    dr.e  = dr.zf + dr.num;
    title = dr.title;
    version = dr.version;
    date = dr.date;
    lsda_read(handle,LSDA_INT,"ids",0,dr.num,dr.ids);
  }
  if(have_p) {
    lsda_cd(handle,"/bndout/pressure/metadata");
    lsda_read(handle,LSDA_I1,"title",0,80,p.title);
    p.title[72]=0;
    lsda_read(handle,LSDA_I1,"version",0,10,p.version);
    p.version[10]=0;
    lsda_read(handle,LSDA_I1,"date",0,10,p.date);
    p.date[10]=0;
    lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
    p.num = length;
    p.ids = (int *) malloc(p.num*sizeof(int));
    p.xf = (float *) malloc(4*p.num*sizeof(float));
    p.yf = p.xf + p.num;
    p.zf = p.yf + p.num;
    p.e  = p.zf + p.num;
    title = p.title;
    version = p.version;
    date = p.date;
    lsda_read(handle,LSDA_INT,"ids",0,p.num,p.ids);
  }
  if(have_vn) {
    lsda_cd(handle,"/bndout/velocity/nodes/metadata");
    lsda_read(handle,LSDA_I1,"title",0,80,vn.title);
    vn.title[72]=0;
    lsda_read(handle,LSDA_I1,"version",0,10,vn.version);
    vn.version[10]=0;
    lsda_read(handle,LSDA_I1,"date",0,10,vn.date);
    vn.date[10]=0;
    lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
    vn.num = length;
    vn.ids = (int *) malloc(vn.num*sizeof(int));
    vn.xf = (float *) malloc(4*vn.num*sizeof(float));
    vn.yf = vn.xf + vn.num;
    vn.zf = vn.yf + vn.num;
    vn.e  = vn.zf + vn.num;
    title = vn.title;
    version = vn.version;
    date = vn.date;
    lsda_read(handle,LSDA_INT,"ids",0,vn.num,vn.ids);
  }
  if(have_vr) {
    lsda_cd(handle,"/bndout/velocity/rigidbodies/metadata");
    lsda_read(handle,LSDA_I1,"title",0,80,vr.title);
    vr.title[72]=0;
    lsda_read(handle,LSDA_I1,"version",0,10,vr.version);
    vr.version[10]=0;
    lsda_read(handle,LSDA_I1,"date",0,10,vr.date);
    vr.date[10]=0;
    lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
    vr.num = length;
    vr.ids = (int *) malloc(vr.num*sizeof(int));
    vr.xf = (float *) malloc(7*vr.num*sizeof(float));
    vr.yf = vr.xf + vr.num;
    vr.zf = vr.yf + vr.num;
    vr.e  = vr.zf + vr.num;
    vr.xm = vr.e  + vr.num;
    vr.ym = vr.xm + vr.num;
    vr.zm = vr.ym + vr.num;
    title = vr.title;
    version = vr.version;
    date = vr.date;
    lsda_read(handle,LSDA_INT,"ids",0,vr.num,vr.ids);
  }

  if(title == NULL) return;  /* huh? */
/*
  open file and write header
*/
  printf("Extracting BNDOUT data\n");
  fp=fopen("bndout","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  k=0;
  if(have_vn) {
    lsda_cd(handle,"/bndout/velocity/nodes/metadata");
    i = have_vr ? 0 : 1;
    k = output_legend(handle,fp,1,i);
  }
  if(have_vr) {
    lsda_cd(handle,"/bndout/velocity/rigidbodies/metadata");
    i = !k;
    output_legend(handle,fp,i,1);
  }
/*
  Loop through time states and write each one
*/
  for(state=1; ; state++) {
    header=0;
    xt = yt = zt = et = 0.;
    if(have_dn && ! bndout_dn(fp,handle,state,&dn,&xt,&yt,&zt,&et,&header)) break;
    if(have_dr && ! bndout_dr(fp,handle,state,&dr,&xt,&yt,&zt,&et,&header)) break;
    if(have_dn || have_dr) {
      fprintf(fp,"              xtotal=%13.4E   ytotal=%13.4E  ztotal=%13.4E   etotal=%13.4E\n",
      xt,yt,zt,et);
    }
    if(have_p && ! bndout_p(fp,handle,state,&p,&header)) break;
    xt = yt = zt = et = 0.;
    if(have_vn && ! bndout_vn(fp,handle,state,&vn,&xt,&yt,&zt,&et,&header)) break;
    if(have_vr && ! bndout_vr(fp,handle,state,&vr,&xt,&yt,&zt,&et,&header)) break;
    if(have_vn || have_vr) {
      fprintf(fp,"              xtotal=%13.4E   ytotal=%13.4E  ztotal=%13.4E   etotal=%13.4E\n",
      xt,yt,zt,et);
    }
  }
  close(fp);
/*
  free everything here....
*/
  if(have_dn) {
    free(dn.ids);
    free(dn.xf);
  }
  if(have_dr) {
    free(dr.ids);
    free(dr.xf);
  }
  if(have_p) {
    free(p.ids);
    free(p.xf);
  }
  if(have_vn) {
    free(vn.ids);
    free(vn.xf);
  }
  if(have_vr) {
    free(vr.ids);
    free(vr.xf);
  }
  printf("      %d states extracted\n",state-1);
}

bndout_dn(FILE *fp,int handle, int state, BND_DATA *dn,
          float *xt, float *yt, float *zt, float *et, int *header)
{
  char dirname[128];
  float time;
  int cycle;
  int typeid, filenum;
  LSDA_Length length;
  int num;
  int i,j,k;

  sprintf(dirname,"/bndout/discrete/nodes/d%6.6d",state);
  lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
  if(typeid != 0) return 0;
  lsda_cd(handle,dirname);
  if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xforce" ,0,dn->num,dn->xf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"x_force",0,dn->num,dn->xf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"yforce" ,0,dn->num,dn->yf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"y_force",0,dn->num,dn->yf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"zforce" ,0,dn->num,dn->zf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"z_force",0,dn->num,dn->zf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"energy",0,dn->num,dn->e)  != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xtotal" ,0,1,xt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"x_total",0,1,xt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ytotal" ,0,1,yt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"y_total",0,1,yt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ztotal" ,0,1,zt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"z_total",0,1,zt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"etotal",0,1,et)  != 1) return 0;
/*
  Output data
*/
  fprintf(fp,"\n\n\n\n\n n o d a l   f o r c e/e n e r g y");
  fprintf(fp,"    o u t p u t   t=%9.3E\n",time);
  *header = 1;
  fprintf(fp,"\n\n\n\n\n discrete nodal point forces \n\n");
  for(i=0; i<dn->num; i++) {
    fprintf(fp," nd#%8d  xforce=%13.4E   yforce=%13.4E  zforce=%13.4E   energy=%13.4E\n",
      dn->ids[i],dn->xf[i],dn->yf[i],dn->zf[i],dn->e[i]);
  }
  return 1;
}
bndout_dr(FILE *fp,int handle, int state, BND_DATA *dn,
          float *xtt, float *ytt, float *ztt, float *ett, int *header)
{
  char dirname[128];
  float time;
  int cycle;
  int typeid, filenum;
  LSDA_Length length;
  int num;
  float xt,yt,zt,et;
  int i,j,k;

  sprintf(dirname,"/bndout/discrete/rigidbodies/d%6.6d",state);
  lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
  if(typeid != 0) return 0;
  lsda_cd(handle,dirname);
  if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xforce" ,0,dn->num,dn->xf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"x_force",0,dn->num,dn->xf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"yforce" ,0,dn->num,dn->yf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"y_force",0,dn->num,dn->yf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"zforce" ,0,dn->num,dn->zf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"z_force",0,dn->num,dn->zf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"energy",0,dn->num,dn->e)  != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xtotal" ,0,1,&xt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"x_total",0,1,&xt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ytotal" ,0,1,&yt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"y_total",0,1,&yt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ztotal" ,0,1,&zt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"z_total",0,1,&zt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"etotal",0,1,&et)  != 1) return 0;
  *xtt += xt;
  *ytt += yt;
  *ztt += zt;
  *ett += et;
/*
  Output data
*/
  if(! *header) {
    fprintf(fp,"\n\n\n\n\n n o d a l   f o r c e/e n e r g y");
    fprintf(fp,"    o u t p u t   t=%9.3E\n",time);
    fprintf(fp,"\n\n\n\n\n discrete nodal point forces \n\n");
  }
  *header = 2;
  for(i=0; i<dn->num; i++) {
    fprintf(fp," mt#%8d  xforce=%13.4E   yforce=%13.4E  zforce=%13.4E   energy=%13.4E\n",
      dn->ids[i],dn->xf[i],dn->yf[i],dn->zf[i],dn->e[i]);
  }
  return 1;
}
bndout_p(FILE *fp,int handle, int state, BND_DATA *dn, int *header)
{
  char dirname[128];
  float time;
  int cycle;
  int typeid, filenum;
  LSDA_Length length;
  int num;
  float xt,yt,zt,et;
  int i,j,k;

  sprintf(dirname,"/bndout/pressure/d%6.6d",state);
  lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
  if(typeid != 0) return 0;
  lsda_cd(handle,dirname);
  if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xforce" ,0,dn->num,dn->xf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"x_force",0,dn->num,dn->xf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"yforce" ,0,dn->num,dn->yf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"y_force",0,dn->num,dn->yf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"zforce" ,0,dn->num,dn->zf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"z_force",0,dn->num,dn->zf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"energy",0,dn->num,dn->e)  != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xtotal" ,0,1,&xt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"x_total",0,1,&xt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ytotal" ,0,1,&yt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"y_total",0,1,&yt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ztotal" ,0,1,&zt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"z_total",0,1,&zt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"etotal",0,1,&et)  != 1) return 0;
/*
  Output data
*/
  fprintf(fp,"\n\n\n\n\n n o d a l   f o r c e/e n e r g y");
  fprintf(fp,"    o u t p u t   t=%9.3E\n",time);
  *header = 3;
  fprintf(fp,"\n\n\n\n\n pressure boundary condition forces \n\n");
  for(i=0; i<dn->num; i++) {
    fprintf(fp," nd#%8d  xforce=%13.4E   yforce=%13.4E  zforce=%13.4E   energy=%13.4E\n",
      dn->ids[i],dn->xf[i],dn->yf[i],dn->zf[i],dn->e[i]);
  }
  fprintf(fp,"              xtotal=%13.4E   ytotal=%13.4E  ztotal=%13.4E   etotal=%13.4E\n",
  xt,yt,zt,et);
  return 1;
}
bndout_vn(FILE *fp,int handle, int state, BND_DATA *dn,
          float *xt, float *yt, float *zt, float *et, int *header)
{
  char dirname[128];
  float time;
  int cycle;
  int typeid, filenum;
  LSDA_Length length;
  int num;
  int i,j,k;

  sprintf(dirname,"/bndout/velocity/nodes/d%6.6d",state);
  lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
  if(typeid != 0) return 0;
  lsda_cd(handle,dirname);
  if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xforce" ,0,dn->num,dn->xf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"x_force",0,dn->num,dn->xf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"yforce" ,0,dn->num,dn->yf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"y_force",0,dn->num,dn->yf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"zforce" ,0,dn->num,dn->zf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"z_force",0,dn->num,dn->zf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"energy",0,dn->num,dn->e)  != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xtotal" ,0,1,xt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"x_total",0,1,xt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ytotal" ,0,1,yt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"y_total",0,1,yt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ztotal" ,0,1,zt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"z_total",0,1,zt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"etotal",0,1,et)  != 1) return 0;
/*
  Output data
*/
  fprintf(fp,"\n\n\n\n\n n o d a l   f o r c e/e n e r g y");
  fprintf(fp,"    o u t p u t   t=%9.3E\n",time);
  *header = 4;
  fprintf(fp,"\n\n\n\n\n velocity boundary condition forces/");
  fprintf(fp,"rigid body moments \n\n");
  for(i=0; i<dn->num; i++) {
    fprintf(fp," nd#%8d  xforce=%13.4E   yforce=%13.4E  zforce=%13.4E   energy=%13.4E\n",
      dn->ids[i],dn->xf[i],dn->yf[i],dn->zf[i],dn->e[i]);
  }
  return 1;
}
bndout_vr(FILE *fp,int handle, int state, BND_DATA *dn,
          float *xtt, float *ytt, float *ztt, float *ett, int *header)
{
  char dirname[128];
  float time;
  int cycle;
  int typeid, filenum;
  LSDA_Length length;
  int num;
  float xt,yt,zt,et;
  int i,j,k;

  sprintf(dirname,"/bndout/velocity/rigidbodies/d%6.6d",state);
  lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
  if(typeid != 0) return 0;
  lsda_cd(handle,dirname);
  if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xforce" ,0,dn->num,dn->xf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"x_force",0,dn->num,dn->xf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"yforce" ,0,dn->num,dn->yf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"y_force",0,dn->num,dn->yf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"zforce" ,0,dn->num,dn->zf) != dn->num &&
     lsda_read(handle,LSDA_FLOAT,"z_force",0,dn->num,dn->zf) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"energy",0,dn->num,dn->e)  != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xmoment",0,dn->num,dn->xm) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ymoment",0,dn->num,dn->ym) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"zmoment",0,dn->num,dn->zm) != dn->num) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"xtotal" ,0,1,&xt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"x_total",0,1,&xt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ytotal" ,0,1,&yt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"y_total",0,1,&yt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"ztotal" ,0,1,&zt)  != 1 &&
     lsda_read(handle,LSDA_FLOAT,"z_total",0,1,&zt)  != 1) return 0;
  if(lsda_read(handle,LSDA_FLOAT,"etotal",0,1,&et)  != 1) return 0;
  *xtt += xt;
  *ytt += yt;
  *ztt += zt;
  *ett += et;
/*
  Output data
*/
  if(*header != 4) {
    fprintf(fp,"\n\n\n\n\n n o d a l   f o r c e/e n e r g y");
    fprintf(fp,"    o u t p u t   t=%9.3E\n",time);
    fprintf(fp,"\n\n\n\n\n velocity boundary condition forces/");
    fprintf(fp,"rigid body moments \n\n");
  }
  *header = 5;
  for(i=0; i<dn->num; i++) {
    fprintf(fp,"mat#%8d  xforce=%13.4E   yforce=%13.4E  zforce=%13.4E   energy=%13.4E\n",
      dn->ids[i],dn->xf[i],dn->yf[i],dn->zf[i],dn->e[i]);
    fprintf(fp,"             xmoment=%13.4E  ymoment=%13.4E zmoment=%13.4E\n",
      dn->xm[i],dn->ym[i],dn->zm[i]);
  }
  return 1;
}
/*
  RBDOUT file
*/
translate_rbdout(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int num_nodal;
  int *ids,cycle;
  float *gx,*gy,*gz;
  float *gdx,*gdy,*gdz,*grdx,*grdy,*grdz;
  float *gvx,*gvy,*gvz,*grvx,*grvy,*grvz;
  float *gax,*gay,*gaz,*grax,*gray,*graz;
  float *ldx,*ldy,*ldz,*lrdx,*lrdy,*lrdz;
  float *lvx,*lvy,*lvz,*lrvx,*lrvy,*lrvz;
  float *lax,*lay,*laz,*lrax,*lray,*lraz;
  float *d11,*d12,*d13,*d21,*d22,*d23,*d31,*d32,*d33;
  float time;
  FILE *fp;

  lsda_cd(handle,"/rbdout/metadata");
  printf("Extracting RBDOUT data\n");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num = length;
  ids = (int *) malloc(num*sizeof(int));
  gx  = (float *) malloc(48*num*sizeof(float));
  gy  = gx   + num;
  gz  = gy   + num;
  gdx = gz   + num;
  gdy = gdx  + num;
  gdz = gdy  + num;
  grdx= gdz  + num;
  grdy= grdx + num;
  grdz= grdy + num;
  gvx = grdz + num;
  gvy = gvx  + num;
  gvz = gvy  + num;
  grvx= gvz  + num;
  grvy= grvx + num;
  grvz= grvy + num;
  gax = grvz + num;
  gay = gax  + num;
  gaz = gay  + num;
  grax= gaz  + num;
  gray= grax + num;
  graz= gray + num;
  ldx = graz + num;
  ldy = ldx  + num;
  ldz = ldy  + num;
  lrdx= ldz  + num;
  lrdy= lrdx + num;
  lrdz= lrdy + num;
  lvx = lrdz + num;
  lvy = lvx  + num;
  lvz = lvy  + num;
  lrvx= lvz  + num;
  lrvy= lrvx + num;
  lrvz= lrvy + num;
  lax = lrvz + num;
  lay = lax  + num;
  laz = lay  + num;
  lrax= laz  + num;
  lray= lrax + num;
  lraz= lray + num;
  d11 = lraz + num;
  d12 = d11  + num;
  d13 = d12  + num;
  d21 = d13  + num;
  d22 = d21  + num;
  d23 = d22  + num;
  d31 = d23  + num;
  d32 = d31  + num;
  d33 = d32  + num;

  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
  lsda_read(handle,LSDA_INT,"num_nodal",0,1,&num_nodal);
/*
  open file and write header
*/
  fp=fopen("rbdout","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/rbdout/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_INT,"cycle",0,1,&cycle) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_x",0,num,gx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_y",0,num,gy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_z",0,num,gz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_dx",0,num,gdx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_dy",0,num,gdy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_dz",0,num,gdz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_rdx",0,num,grdx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_rdy",0,num,grdy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_rdz",0,num,grdz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_vx",0,num,gvx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_vy",0,num,gvy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_vz",0,num,gvz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_rvx",0,num,grvx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_rvy",0,num,grvy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_rvz",0,num,grvz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_ax",0,num,gax) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_ay",0,num,gay) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_az",0,num,gaz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_rax",0,num,grax) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_ray",0,num,gray) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"global_raz",0,num,graz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dircos_11",0,num,d11) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dircos_12",0,num,d12) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dircos_13",0,num,d13) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dircos_21",0,num,d21) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dircos_22",0,num,d22) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dircos_23",0,num,d23) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dircos_31",0,num,d31) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dircos_32",0,num,d32) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"dircos_33",0,num,d33) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_dx",0,num,ldx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_dy",0,num,ldy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_dz",0,num,ldz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_rdx",0,num,lrdx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_rdy",0,num,lrdy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_rdz",0,num,lrdz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_vx",0,num,lvx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_vy",0,num,lvy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_vz",0,num,lvz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_rvx",0,num,lrvx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_rvy",0,num,lrvy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_rvz",0,num,lrvz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_ax",0,num,lax) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_ay",0,num,lay) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_az",0,num,laz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_rax",0,num,lrax) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_ray",0,num,lray) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"local_raz",0,num,lraz) != num) break;

    fprintf(fp,"1\n\n  r i g i d   b o d y   m o t i o n   a t  cycle=%8d    time=%15.6E\n",cycle,time);
    for(i=0; i<num; i++) {
      if(i < num-num_nodal)
        fprintf(fp,"\n rigid body%8d\n",ids[i]);
      else
        fprintf(fp," nodal rigid body%8d\n",ids[i]);
      fprintf(fp,"   global             x           y           z");
      fprintf(fp,"          x-rot       y-rot       z-rot\n");
      fprintf(fp,"   coordinates:  %12.4E%12.4E%12.4E\n",gx[i],gy[i],gz[i]);
      fprintf(fp," displacements:  %12.4E%12.4E%12.4E%12.4E%12.4E%12.4E\n",
        gdx[i],gdy[i],gdz[i],grdx[i],grdy[i],grdz[i]);
      fprintf(fp,"    velocities:  %12.4E%12.4E%12.4E%12.4E%12.4E%12.4E\n",
        gvx[i],gvy[i],gvz[i],grvx[i],grvy[i],grvz[i]);
      fprintf(fp," accelerations:  %12.4E%12.4E%12.4E%12.4E%12.4E%12.4E\n",
        gax[i],gay[i],gaz[i],grax[i],gray[i],graz[i]);
      fprintf(fp,"\nprincipal or user defined local coordinate direction vectors\n");
      fprintf(fp,"                     a           b           c\n");
      fprintf(fp,"     row 1%15.4E%15.4E%15.4E\n",d11[i],d12[i],d13[i]);
      fprintf(fp,"     row 2%15.4E%15.4E%15.4E\n",d21[i],d22[i],d23[i]);
      fprintf(fp,"     row 3%15.4E%15.4E%15.4E\n\n",d31[i],d32[i],d33[i]);
      fprintf(fp," output in principal or user defined local coordinate directions\n");
      fprintf(fp,"                      a           b           c          ");
      fprintf(fp,"a-rot       b-rot       c-rot\n");
      fprintf(fp," displacements:  %12.4E%12.4E%12.4E%12.4E%12.4E%12.4E\n",
        ldx[i],ldy[i],ldz[i],lrdx[i],lrdy[i],lrdz[i]);
      fprintf(fp,"    velocities:  %12.4E%12.4E%12.4E%12.4E%12.4E%12.4E\n",
        lvx[i],lvy[i],lvz[i],lrvx[i],lrvy[i],lrvz[i]);
      fprintf(fp," accelerations:  %12.4E%12.4E%12.4E%12.4E%12.4E%12.4E\n",
        lax[i],lay[i],laz[i],lrax[i],lray[i],lraz[i]);
    }

  }
  fclose(fp);
  free(gx);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  GCEOUT file
*/
translate_gceout(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int num_nodal;
  int *ids;
  float *xf,*yf,*zf,*xm,*ym,*zm,*tf,*tm;
  float time;
  FILE *fp;

  lsda_cd(handle,"/gceout/metadata");
  printf("Extracting GCEOUT data\n");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num = length;
  ids = (int *) malloc(num*sizeof(int));
  xf  = (float *) malloc(8*num*sizeof(float));
  yf  = xf   + num;
  zf  = yf   + num;
  xm  = zf   + num;
  ym  = xm   + num;
  zm  = ym   + num;
  tf  = zm   + num;
  tm  = tf   + num;

  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
/*
  open file and write header
*/
  fp=fopen("gceout","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  fprintf(fp,"\n\n\n\n c o n t a c t   e n t i t i e s   r e s u l t");
  fprintf(fp," a n t s\n\n\n\n");
  fprintf(fp,"       material#   time      x-force     y-force     z-force");
  fprintf(fp,"    magnitude\n");
  fprintf(fp,"line#2  resultant moments    x-moment    y-moment    z-moment");
  fprintf(fp,"   magnitude\n");
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/gceout/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_force",         0,num,xf) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_force",         0,num,yf) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_force",         0,num,zf) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"x_moment",        0,num,xm) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_moment",        0,num,ym) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_moment",        0,num,zm) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"force_magnitude", 0,num,tf) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"moment_magnitude",0,num,tm) != num) break;
    for(i=0; i<num; i++) {
      fprintf(fp,"%12d  %12.4E%12.4E%12.4E%12.4E%12.4E\n",
       ids[i],time,xf[i],yf[i],zf[i],tf[i]);
      fprintf(fp,"                          %12.4E%12.4E%12.4E%12.4E\n",
       xm[i],ym[i],zm[i],tm[i]);
    }
    fprintf(fp,"\n");
  }
  fclose(fp);
  free(xf);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  SLEOUT file
*/
translate_sleout(int handle)
{
  int i,j,k,typeid,num,numm,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *ids,*single_sided;
  float *slave, *master;
  float time,ts,tm,te;
  int cycle;
  FILE *fp;

  lsda_cd(handle,"/sleout/metadata");
  printf("Extracting SLEOUT data\n");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num = length;
  ids          = (int *) malloc(num*sizeof(int));
  single_sided = (int *) malloc(num*sizeof(int));
  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
  lsda_read(handle,LSDA_INT,"single_sided",0,num,single_sided);
  numm = num;
  for(i=0; i<num; i++)
    if(single_sided[i]) numm--;
  slave  = (float *) malloc(num *sizeof(float));
  master = (float *) malloc(numm*sizeof(float));
/*
  open file and write header
*/
  fp=fopen("sleout","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/sleout/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_INT,"cycle",0,1,&cycle) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"slave",0,num,slave) != num) break;
    if(numm > 0 &&
       lsda_read(handle,LSDA_FLOAT,"master",0,numm,master) != numm) break;
    if(lsda_read(handle,LSDA_FLOAT,"total_slave",0,1,&ts) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"total_master",0,1,&tm) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"total_energy",0,1,&te) != 1) break;

    fprintf(fp,"\n\n\n contact interface energy file, time=%14.7E\n",time);
    fprintf(fp,"    #            slave       master        cycle=%14d\n\n",cycle);
    for(i=j=0; i<num; i++) {
      if(single_sided[i])
        fprintf(fp,"%10d%13.4E\n",ids[i],slave[i]);
      else
        fprintf(fp,"%10d%13.4E%13.4E\n",ids[i],slave[i],master[j++]);
    }
    fprintf(fp,"\n summary   total slave side=%14.7E\n",ts);
    fprintf(fp,  "           total mastr side=%14.7E\n",tm);
    fprintf(fp,  "           total energy    =%14.7E\n\n\n\n",te);
  }
  fclose(fp);
  free(master);
  free(slave);
  free(single_sided);
  free(ids);
  printf("      %d states extracted\n",state-1);
}
/*
  SBTOUT file
*/
translate_sbtout(int handle)
{
  int i,j,k,typeid,filenum,state;
  int numb,nums,numr;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *bids,*sids,*rids;
  float *blength,*bforce,*slip,*pullout,*rforce;
  float time;
  int cycle;
  FILE *fp;

  lsda_cd(handle,"/sbtout/metadata");
  printf("Extracting SBTOUT data\n");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"belt_ids",&typeid,&length,&filenum);
  numb = length;
  bids  = (int *) malloc(numb*sizeof(int));
  blength = (float *) malloc(numb*sizeof(float));
  bforce = (float *) malloc(numb*sizeof(float));
  lsda_read(handle,LSDA_INT,"belt_ids",0,numb,bids);
  lsda_queryvar(handle,"slipring_ids",&typeid,&length,&filenum);
  nums = length;
  if(nums > 0) {
    sids  = (int *) malloc(nums*sizeof(int));
    slip  = (float *) malloc(nums*sizeof(float));
    lsda_read(handle,LSDA_INT,"slipring_ids",0,nums,sids);
  }
  lsda_queryvar(handle,"retractor_ids",&typeid,&length,&filenum);
  numr = length;
  if(numr > 0) {
    rids  = (int *) malloc(numr*sizeof(int));
    pullout  = (float *) malloc(numr*sizeof(float));
    rforce  = (float *) malloc(numr*sizeof(float));
    lsda_read(handle,LSDA_INT,"retractor_ids",0,numr,rids);
  }
/*
  open file and write header
*/
  fp=fopen("sbtout","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  fprintf(fp,"\n\n\n\n S E A T B E L T    O U T P U T\n\n");
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/sbtout/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"belt_force",0,numb,bforce) != numb) break;
    if(lsda_read(handle,LSDA_FLOAT,"belt_length",0,numb,blength) != numb) break;
    if(nums && lsda_read(handle,LSDA_FLOAT,"ring_slip",0,nums,slip) != nums) break;
    if(numr) {
      if(lsda_read(handle,LSDA_FLOAT,"retractor_pull_out",0,numr,pullout) != numr) break;
      if(lsda_read(handle,LSDA_FLOAT,"retractor_force",0,numr,rforce) != numr) break;
    }

    fprintf(fp,"\n\n time...........................%16.5E\n",time);
    for(i=0; i<numb; i++) {
      fprintf(fp,"\n seat belt number...............%8d\n",bids[i]);
      fprintf(fp,  " force..........................%16.5E\n",bforce[i]);
      fprintf(fp,  " current length.................%16.5E\n",blength[i]);
    }
    for(i=0; i<nums; i++) {
      fprintf(fp,"\n slip ring number...............%8d\n",sids[i]);
      fprintf(fp,  " total slip from side 1 to .....%16.5E\n",slip[i]);
    }
    for(i=0; i<numr; i++) {
      fprintf(fp,"\n retractor number...............%8d\n",rids[i]);
      fprintf(fp,  " pull-out to date...............%14.5E\n",pullout[i]);
      fprintf(fp,  " force in attached element......%14.5E\n",rforce[i]);
    }
  }
  fclose(fp);
  if(numr > 0) {
    free(rforce);
    free(pullout);
    free(rids);
  }
  if(nums > 0) {
    free(slip);
    free(sids);
  }
  free(bforce);
  free(blength);
  free(bids);
  printf("      %d states extracted\n",state-1);
}
/*
  JNTFORC file
*/
translate_jntforc(int handle)
{
  int i,j,k,typeid,filenum,state;
  int numj,num0,num1;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *idj,*local,*id0,*id1;
  float *xf,*yf,*zf,*xm,*ym,*zm,*rf,*rm;
  float *p0,*dpdt0,*t0,*dtdt0,*s0,*dsdt0;
  float *ps0,*pd0,*pt0,*ts0,*td0,*tt0,*ss0,*sd0,*st0,*je0;
  float *a1,*dadt1,*g1,*dgdt1,*b1,*dbdt1;
  float *as1,*ad1,*at1,*gsf1,*bs1,*bd1,*bt1,*je1;
  float time;
  FILE *fp;

  lsda_cd(handle,"/jntforc/metadata");
  printf("Extracting JNTFORC data\n");
/*
  Read metadata
*/
  lsda_queryvar(handle,"/jntforc/joints",&typeid,&length,&filenum);
  if(typeid == 0) {
    lsda_cd(handle,"/jntforc/joints/metadata");
    lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
    numj = length;
    lsda_read(handle,LSDA_I1,"title",0,80,title);
    lsda_read(handle,LSDA_I1,"version",0,10,version);
    lsda_read(handle,LSDA_I1,"date",0,10,date);
    title[72]=0;
    version[10]=0;
    date[10]=0;
    idj  = (int *) malloc(numj*sizeof(int));
    local  = (int *) malloc(numj*sizeof(int));
    xf  = (float *) malloc(numj*sizeof(float));
    yf  = (float *) malloc(numj*sizeof(float));
    zf  = (float *) malloc(numj*sizeof(float));
    xm  = (float *) malloc(numj*sizeof(float));
    ym  = (float *) malloc(numj*sizeof(float));
    zm  = (float *) malloc(numj*sizeof(float));
    rf  = (float *) malloc(numj*sizeof(float));
    rm  = (float *) malloc(numj*sizeof(float));
    lsda_read(handle,LSDA_INT,"ids",0,numj,idj);
    lsda_read(handle,LSDA_INT,"local",0,numj,local);
  } else {
    numj = 0;
  }
  lsda_queryvar(handle,"/jntforc/type0",&typeid,&length,&filenum);
  if(typeid == 0) {
    lsda_cd(handle,"/jntforc/type0/metadata");
    lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
    num0 = length;
    lsda_read(handle,LSDA_I1,"title",0,80,title);
    lsda_read(handle,LSDA_I1,"version",0,10,version);
    lsda_read(handle,LSDA_I1,"date",0,10,date);
    title[72]=0;
    version[10]=0;
    date[10]=0;
    id0  = (int *) malloc(num0*sizeof(int));
    p0    = (float *) malloc(num0*sizeof(float));
    dpdt0 = (float *) malloc(num0*sizeof(float));
    t0    = (float *) malloc(num0*sizeof(float));
    dtdt0 = (float *) malloc(num0*sizeof(float));
    s0    = (float *) malloc(num0*sizeof(float));
    dsdt0 = (float *) malloc(num0*sizeof(float));
    ps0   = (float *) malloc(num0*sizeof(float));
    pd0   = (float *) malloc(num0*sizeof(float));
    pt0   = (float *) malloc(num0*sizeof(float));
    ts0   = (float *) malloc(num0*sizeof(float));
    td0   = (float *) malloc(num0*sizeof(float));
    tt0   = (float *) malloc(num0*sizeof(float));
    ss0   = (float *) malloc(num0*sizeof(float));
    sd0   = (float *) malloc(num0*sizeof(float));
    st0   = (float *) malloc(num0*sizeof(float));
    je0   = (float *) malloc(num0*sizeof(float));
    lsda_read(handle,LSDA_INT,"ids",0,num0,id0);
  } else {
    num0 = 0;
  }
  lsda_queryvar(handle,"/jntforc/type1",&typeid,&length,&filenum);
  if(typeid == 0) {
    lsda_cd(handle,"/jntforc/type1/metadata");
    lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
    num1 = length;
    lsda_read(handle,LSDA_I1,"title",0,80,title);
    lsda_read(handle,LSDA_I1,"version",0,10,version);
    lsda_read(handle,LSDA_I1,"date",0,10,date);
    title[72]=0;
    version[10]=0;
    date[10]=0;
    id1  = (int *) malloc(num0*sizeof(int));
    a1    = (float *) malloc(num1*sizeof(float));
    dadt1 = (float *) malloc(num1*sizeof(float));
    g1    = (float *) malloc(num1*sizeof(float));
    dgdt1 = (float *) malloc(num1*sizeof(float));
    b1    = (float *) malloc(num1*sizeof(float));
    dbdt1 = (float *) malloc(num1*sizeof(float));
    as1   = (float *) malloc(num1*sizeof(float));
    ad1   = (float *) malloc(num1*sizeof(float));
    at1   = (float *) malloc(num1*sizeof(float));
    gsf1  = (float *) malloc(num1*sizeof(float));
    bs1   = (float *) malloc(num1*sizeof(float));
    bd1   = (float *) malloc(num1*sizeof(float));
    bt1   = (float *) malloc(num1*sizeof(float));
    je1   = (float *) malloc(num1*sizeof(float));
    lsda_read(handle,LSDA_INT,"ids",0,num1,id1);
  } else {
    num1 = 0;
  }
/*
  open file and write header
*/
  fp=fopen("jntforc","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  k=0;
  if(numj > 0) {
    lsda_cd(handle,"/jntforc/joints/metadata");
    i=(num0+num1 > 0) ? 0 : 1;
    k = output_legend(handle,fp,1,i);
  }
  if(num0 > 0) {
    lsda_cd(handle,"/jntforc/type0/metadata");
    i=!k;
    j=(num1 > 0) ? 0 : 1;
    k = output_legend(handle,fp,i,j) || k;
  }
  if(num0 > 1) {
    lsda_cd(handle,"/jntforc/type1/metadata");
    i= !k;
    output_legend(handle,fp,i,1);
  }
/*
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    if(numj > 0) {
      sprintf(dirname,"/jntforc/joints/d%6.6d",state);
      lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
      if(typeid != 0) break;
      lsda_cd(handle,dirname);
      if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
      if(lsda_read(handle,LSDA_FLOAT,"x_force",         0,numj,xf) != numj) break;
      if(lsda_read(handle,LSDA_FLOAT,"y_force",         0,numj,yf) != numj) break;
      if(lsda_read(handle,LSDA_FLOAT,"z_force",         0,numj,zf) != numj) break;
      if(lsda_read(handle,LSDA_FLOAT,"x_moment",        0,numj,xm) != numj) break;
      if(lsda_read(handle,LSDA_FLOAT,"y_moment",        0,numj,ym) != numj) break;
      if(lsda_read(handle,LSDA_FLOAT,"z_moment",        0,numj,zm) != numj) break;
      if(lsda_read(handle,LSDA_FLOAT,"resultant_force", 0,numj,rf) != numj) break;
      if(lsda_read(handle,LSDA_FLOAT,"resultant_moment",0,numj,rm) != numj) break;
      fprintf(fp,"\n\n time.........................%14.5E\n",time);
      for(i=0; i<numj; i++) {
        fprintf(fp," joint number.................%10d\n",idj[i]);
        if(local[i]) {
          fprintf(fp," x-force  (local) ............%14.5E\n",xf[i]);
          fprintf(fp," y-force  (local) ............%14.5E\n",yf[i]);
          fprintf(fp," z-force  (local) ............%14.5E\n",zf[i]);
          fprintf(fp," x-moment (local) ............%14.5E\n",xm[i]);
          fprintf(fp," y-moment (local) ............%14.5E\n",ym[i]);
          fprintf(fp," z-moment (local) ............%14.5E\n",zm[i]);
        } else {
          fprintf(fp," x-force......................%14.5E\n",xf[i]);
          fprintf(fp," y-force......................%14.5E\n",yf[i]);
          fprintf(fp," z-force......................%14.5E\n",zf[i]);
          fprintf(fp," x-moment.....................%14.5E\n",xm[i]);
          fprintf(fp," y-moment.....................%14.5E\n",ym[i]);
          fprintf(fp," z-moment.....................%14.5E\n",zm[i]);
        }
        fprintf(fp," resultant force..............%14.5E\n",rf[i]);
        fprintf(fp," resultant moment.............%14.5E\n",rm[i]);
      }
    }
    if(num0 > 0) {
      sprintf(dirname,"/jntforc/type0/d%6.6d",state);
      lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
      if(typeid != 0) break;
      lsda_cd(handle,dirname);
      if(lsda_read(handle,LSDA_FLOAT,"phi_degrees",           0,num0,   p0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"d(phi)_dt",             0,num0,dpdt0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"theta_degrees",         0,num0,   t0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"d(theta)_dt",           0,num0,dtdt0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"psi_degrees",           0,num0,   s0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"d(psi)_dt",             0,num0,dsdt0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"phi_moment_stiffness",  0,num0,  ps0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"phi_moment_damping",    0,num0,  pd0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"phi_moment_total",      0,num0,  pt0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"theta_moment_stiffness",0,num0,  ts0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"theta_moment_damping",  0,num0,  td0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"theta_moment_total",    0,num0,  tt0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"psi_moment_stiffness",  0,num0,  ss0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"psi_moment_damping",    0,num0,  sd0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"psi_moment_total",      0,num0,  st0) != num0) break;
      if(lsda_read(handle,LSDA_FLOAT,"joint_energy",          0,num0,  je0) != num0) break;
      for(i=0; i<num0; i++) {
        fprintf(fp," joint stiffness id number....%10d\n",id0[i]);
        fprintf(fp," phi (degrees)................%14.5E\n",p0[i]);
        fprintf(fp," d(phi)/dt (degrees)..........%14.5E\n",dpdt0[i]);
        fprintf(fp," theta (degrees)..............%14.5E\n",t0[i]);
        fprintf(fp," d(theta)/dt (degrees)........%14.5E\n",dtdt0[i]);
        fprintf(fp," psi (degrees)................%14.5E\n",s0[i]);
        fprintf(fp," d(psi)/dt (degrees)..........%14.5E\n",dsdt0[i]);
        fprintf(fp," phi moment-stiffness.........%14.5E\n",ps0[i]);
        fprintf(fp," phi moment-damping...........%14.5E\n",pd0[i]);
        fprintf(fp," phi moment-total.............%14.5E\n",pt0[i]);
        fprintf(fp," theta-moment-stiffness.......%14.5E\n",ts0[i]);
        fprintf(fp," theta-moment-damping.........%14.5E\n",td0[i]);
        fprintf(fp," theta-moment-total...........%14.5E\n",tt0[i]);
        fprintf(fp," psi-moment-stiffness.........%14.5E\n",ss0[i]);
        fprintf(fp," psi-moment-damping...........%14.5E\n",sd0[i]);
        fprintf(fp," psi-moment-total.............%14.5E\n",st0[i]);
        fprintf(fp," joint energy.................%14.5E\n",je0[i]);
      }
    }
    if(num1 > 0) {
      sprintf(dirname,"/jntforc/type1/d%6.6d",state);
      lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
      if(typeid != 0) break;
      lsda_cd(handle,dirname);
      if(lsda_read(handle,LSDA_FLOAT,"alpha_degrees",         0,num1,   a1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"d(alpha)_dt",           0,num1,dadt1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"gamma_degrees",         0,num1,   g1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"d(gamma)_dt",           0,num1,dgdt1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"beta_degrees",          0,num1,   b1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"d(beta)_dt",            0,num1,dbdt1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"alpha_moment_stiffness",0,num1,  as1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"alpha_moment_damping",  0,num1,  ad1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"alpha_moment_total",    0,num1,  at1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"gamma_scale_factor",    0,num1, gsf1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"beta_moment_stiffness", 0,num1,  bs1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"beta_moment_damping",   0,num1,  bd1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"beta_moment_total",     0,num1,  bt1) != num1) break;
      if(lsda_read(handle,LSDA_FLOAT,"joint_energy",          0,num1,  je1) != num1) break;
      for(i=0; i<num1; i++) {
        fprintf(fp," joint stiffness id number....%10d\n",id1[i]);
        fprintf(fp," alpha (degrees)..............%14.5E\n",a1[i]);
        fprintf(fp," d(alpha)/dt (degrees)........%14.5E\n",dadt1[i]);
        fprintf(fp," gamma (degrees)..............%14.5E\n",g1[i]);
        fprintf(fp," d(gamma)/dt (degrees)........%14.5E\n",dgdt1[i]);
        fprintf(fp," beta (degrees)...............%14.5E\n",b1[i]);
        fprintf(fp," d(beta)/dt (degrees).........%14.5E\n",dbdt1[i]);
        fprintf(fp," alpha-moment-stiffness.......%14.5E\n",as1[i]);
        fprintf(fp," alpha-moment-damping.........%14.5E\n",ad1[i]);
        fprintf(fp," alpha-moment-total...........%14.5E\n",at1[i]);
        fprintf(fp," gamma scale factor...........%14.5E\n",gsf1[i]);
        fprintf(fp," beta-moment-stiffness........%14.5E\n",bs1[i]);
        fprintf(fp," beta-moment-damping..........%14.5E\n",bd1[i]);
        fprintf(fp," beta-moment-total............%14.5E\n",bt1[i]);
        fprintf(fp," joint energy.................%14.5E\n",je1[i]);
      }
    }
  }
  fclose(fp);
  if(num1 > 0) {
    free(je1);
    free(bt1);
    free(bd1);
    free(bs1);
    free(gsf1);
    free(at1);
    free(ad1);
    free(as1);
    free(dbdt1);
    free(b1);
    free(dgdt1);
    free(g1);
    free(dadt1);
    free(a1);
    free(id1);
  }
  if(num0 > 0) {
    free(je0);
    free(st0);
    free(sd0);
    free(ss0);
    free(tt0);
    free(td0);
    free(ts0);
    free(pt0);
    free(pd0);
    free(ps0);
    free(dsdt0);
    free(s0);
    free(dtdt0);
    free(t0);
    free(dpdt0);
    free(p0);
    free(id0);
  }
  if(numj > 0) {
    free(rm);
    free(rf);
    free(zm);
    free(ym);
    free(xm);
    free(zf);
    free(yf);
    free(xf);
    free(local);
    free(idj);
  }
  printf("      %d states extracted\n",state-1);
}
/*
  SPHOUT file
*/
translate_sphout(int handle)
{
  int i,j,k,typeid,num,filenum,state;
  LSDA_Length length;
  char dirname[128];
  char title[81];
  char version[11];
  char date[11];
  int *ids,*mat;
  int cycle,have_rot;
  float time;
  float *sig_xx,*sig_yy,*sig_zz;
  float *sig_xy,*sig_yz,*sig_zx;
  float *eps_xx,*eps_yy,*eps_zz;
  float *eps_xy,*eps_yz,*eps_zx;
  float *density,*smooth;
  int *neigh,*act,*nstate;
  float *yield,*effsg;
  char states[5][16];
  FILE *fp;

  lsda_cd(handle,"/sphout/metadata");
  printf("Extracting SPHOUT data\n");
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num=length;


/*
  allocate memory to read in 1 state
*/
  ids    = (int *) malloc(num*sizeof(int));
  mat    = (int *) malloc(num*sizeof(int));
  sig_xx = (float *) malloc(num*sizeof(float));
  sig_yy = (float *) malloc(num*sizeof(float));
  sig_zz = (float *) malloc(num*sizeof(float));
  sig_xy = (float *) malloc(num*sizeof(float));
  sig_yz = (float *) malloc(num*sizeof(float));
  sig_zx = (float *) malloc(num*sizeof(float));
  eps_xx = (float *) malloc(num*sizeof(float));
  eps_yy = (float *) malloc(num*sizeof(float));
  eps_zz = (float *) malloc(num*sizeof(float));
  eps_xy = (float *) malloc(num*sizeof(float));
  eps_yz = (float *) malloc(num*sizeof(float));
  eps_zx = (float *) malloc(num*sizeof(float));
  density= (float *) malloc(num*sizeof(float));
  smooth = (float *) malloc(num*sizeof(float));
  yield  = (float *) malloc(num*sizeof(float));
  effsg  = (float *) malloc(num*sizeof(float));
  act    = (int *) malloc(num*sizeof(int));
  neigh  = (int *) malloc(num*sizeof(int));
  nstate = (int *) malloc(num*sizeof(int));

/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
  lsda_read(handle,LSDA_INT,"mat",0,num,mat);
  lsda_queryvar(handle,"states",&typeid,&length,&filenum);
  lsda_read(handle,LSDA_I1,"states",0,length,dirname);
  for(i=j=k=0; i<length; i++) {
    if(dirname[i] == ',') {
      states[j][k]=0;
      j++;
      k=0;
    } else {
      states[j][k++]=dirname[i];
    }
  }
  states[j][k]=0;
/*
  open file and write header
*/
  fp=fopen("sphout","w");
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  output_legend(handle,fp,1,1);
/*
  Loop through time states and write each one
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/sphout/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"time",0,1,&time) != 1) break;
    if(lsda_read(handle,LSDA_INT,"cycle",0,1,&cycle) != 1) break;
    if(lsda_read(handle,LSDA_FLOAT,"sig_xx",0,num,sig_xx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"sig_yy",0,num,sig_yy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"sig_zz",0,num,sig_zz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"sig_xy",0,num,sig_xy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"sig_yz",0,num,sig_yz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"sig_zx",0,num,sig_zx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"eps_xx",0,num,eps_xx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"eps_yy",0,num,eps_yy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"eps_zz",0,num,eps_zz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"eps_xy",0,num,eps_xy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"eps_yz",0,num,eps_yz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"eps_zx",0,num,eps_zx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"density",0,num,density) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"smooth",0,num,smooth) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"yield",0,num,yield) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"effsg",0,num,effsg) != num) break;
    if(lsda_read(handle,LSDA_INT,"neigh",0,num,neigh) != num) break;
    if(lsda_read(handle,LSDA_INT,"act",0,num,act) != num) break;
    if(lsda_read(handle,LSDA_INT,"state",0,num,nstate) != num) break;

    fprintf(fp,"\n\n\n S P H   o u t p u t       at time%11.4E",time);
    fprintf(fp,"     for  time  step%10d\n",cycle);
    fprintf(fp,"\n particle  mat    sig-xx      sig-yy      sig-zz");
    fprintf(fp,"      sig-xy      sig-yz      sig-zx  \n");
    for(i=0; i<num; i++) {
      fprintf(fp,"%8d%6d",ids[i],mat[i]);
      fprintf(fp,"%12.4E%12.4E%12.4E%12.4E%12.4E%12.4E\n",
          sig_xx[i],sig_yy[i],sig_zz[i],sig_xy[i],sig_yz[i],sig_zx[i]);
    }
    fprintf(fp,"\n particle  mat    eps-xx      eps-yy      eps-zz");
    fprintf(fp,"      eps-xy      eps-yz      eps-zx \n");
    for(i=0; i<num; i++) {
      fprintf(fp,"%8d%6d",ids[i],mat[i]);
      fprintf(fp,"%12.4E%12.4E%12.4E%12.4E%12.4E%12.4E\n",
          eps_xx[i],eps_yy[i],eps_zz[i],eps_xy[i],eps_yz[i],eps_zx[i]);
    }
    fprintf(fp,"\n particle  mat    density     smooth     neigh   act\n");
    for(i=0; i<num; i++) {
      fprintf(fp,"%8d%6d",ids[i],mat[i]);
      fprintf(fp,"%12.4E%12.4E%7d%6d\n",density[i],smooth[i],neigh[i],act[i]);
    }
    fprintf(fp,"\n particle  mat    yield       effsg       state \n");
    for(i=0; i<num; i++) {
      fprintf(fp,"%8d%6d",ids[i],mat[i]);
      fprintf(fp,"%12.4E%12.4E   %7s\n",yield[i],effsg[i],states[nstate[i]]);
    }
  }
  fclose(fp);
  free(ids);
  free(mat);
  free(sig_xx);
  free(sig_yy);
  free(sig_zz);
  free(sig_xy);
  free(sig_yz);
  free(sig_zx);
  free(eps_xx);
  free(eps_yy);
  free(eps_zz);
  free(eps_xy);
  free(eps_yz);
  free(eps_zx);
  free(density);
  free(smooth);
  free(yield);
  free(effsg);
  free(act);
  free(neigh);
  free(nstate);
  printf("      %d states extracted\n",state-1);
}
/*
  DEFGEO file
*/
translate_defgeo(int handle)
{
  int i,j,k,typeid,num,numm,filenum,state;
  LSDA_Length length;
  char dirname[256];
  char title[81];
  char version[11];
  char date[11];
  int *ids,*single_sided;
  float *dx,*dy,*dz;
  float maxdisp;
  float time,ts,tm,te;
  int cycle;
  FILE *fp;
  char *defgeoenv, *outtype;
/*
   now try to find out which format should output
   LSTC_DEFGEO 0        - ls-dyna format
               chrysler - Chrysler format
*/
defgeoenv = (char *) malloc(20);
outtype   = (char *) malloc(20);

defgeoenv = "LSTC_DEFGEO";
outtype   = (char *) getenv(defgeoenv);

  lsda_cd(handle,"/defgeo/metadata");
  printf("Extracting DEFGEO data - ");
/*
  Read metadata
*/
  lsda_read(handle,LSDA_I1,"title",0,80,title);
  lsda_read(handle,LSDA_I1,"version",0,10,version);
  lsda_read(handle,LSDA_I1,"date",0,10,date);
  title[72]=0;
  version[10]=0;
  date[10]=0;
  lsda_queryvar(handle,"ids",&typeid,&length,&filenum);
  num = length;
  ids          = (int   *) malloc(num*sizeof(int));
  dx           = (float *) malloc(num*sizeof(float));
  dy           = (float *) malloc(num*sizeof(float));
  dz           = (float *) malloc(num*sizeof(float));
  lsda_read(handle,LSDA_INT,"ids",0,num,ids);
/*
  open file and write header
*/
  fp=fopen("defgeo","w");
/*
  fprintf(fp," %s\n",title);
  fprintf(fp,"                         ls-dyna (version %s)     date %s\n",version,date);
  Loop through time states and write each one.
*/
  for(state=1; ; state++) {
    sprintf(dirname,"/defgeo/d%6.6d",state);
    lsda_queryvar(handle,dirname,&typeid,&length,&filenum);
    if(typeid != 0) break;
    lsda_cd(handle,dirname);
    if(lsda_read(handle,LSDA_FLOAT,"x_displacement",0,num,dx) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"y_displacement",0,num,dy) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"z_displacement",0,num,dz) != num) break;
    if(lsda_read(handle,LSDA_FLOAT,"max_displacement",0,1,&maxdisp) != 1) break;

    cycle = 1000 + state - 1;
    if(outtype!=NULL && (outtype[0]=='c' || outtype[0]=='C' || outtype[0]=='1')) {
    /* Chrysler format */
    if(state==1) {
    printf("Chrysler format\n");
    fprintf(fp,"$LABEL\n");
    fprintf(fp,"LS      DYNA3D              89P1\n");
    }

    fprintf(fp,"$DISPLACEMENTS\n\n\n\n");
    fprintf(fp,"%8d%8d%8d       0%8d       1       3       1       1\n",
    (int)cycle,(int)num,(int)cycle,(int)cycle);
    fprintf(fp,"%16.7e%16.7e%16.7e%16.7e\n",maxdisp,0.,0.,0.);
    for(j=0; j<num; j++)
      fprintf(fp,"%8d%16.7e%16.7e%16.7e\n",(int)ids[j],dx[j],dy[j],dz[j]);
  } else {
  /* LS-DYNA format */
  if(state==1) printf("LS-DYNA format\n");
    fprintf(fp,"  6000     1%6d                                              %8d\n",
      (int)cycle,(int)num);

    for(j=0; j<num; j++)
      fprintf(fp,"%8d%8.2g%8.2g%8.2g\n",(int)ids[j],dx[j],dy[j],dz[j]);
  }
  }
  fclose(fp);
  free(dx);
  free(dy);
  free(dz);
  free(ids);
  printf("      %d states extracted\n",state-1);
}

