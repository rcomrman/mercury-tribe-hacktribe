/* Reuse R2 native heap, native graphics and Mercury fixture unchanged. */
#define R2_CASE 12
#define main r2_unused_main
#include "../recovery_r2/lifecycle.c"
#undef main
#ifndef NIGHT_CASE
#define NIGHT_CASE 0
#endif
static uint32_t manager[32];
static uint8_t reference[1024];
static void change(unsigned id){FN(void(*)(void*,unsigned,unsigned),0xc006e8bc)(manager,id,0);parent=(void*)(uintptr_t)manager[4];}
static void draw(void){r2_iteration(parent);}
static void clear(void){FN(void(*)(void),0xc0015804)();}
static void match(void){for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==reference[i],106);}
static void cleanup_clear(struct mercury*m){mercury_cleanup(m);clear();}
int main(void){
 init();
 /* Independent native page29 reference on cleared source. */
 parent=FN(void*(*)(unsigned,unsigned),0xc006e664)(29,0);draw();
 for(unsigned i=0;i<1024;i++)reference[i]=fb[i];snap(900);destroy(parent,1);clear();
 parent=FN(void*(*)(unsigned,unsigned),0xc006e664)(25,0);manager[4]=(uintptr_t)parent;manager[7]=25;
 if(NIGHT_CASE!=0){struct mercury*m=new_mercury(0);append(parent,m);if(NIGHT_CASE==2||NIGHT_CASE==6)mercury_vt[4]=(uintptr_t)cleanup_clear;}
 draw();snap(0);
 if(NIGHT_CASE==4){((uint8_t*)manager)[93]=1;void*before=parent;change(29);REQUIRE(parent==before&&manager[7]==25,107);snap(4);((uint8_t*)manager)[93]=0;}
 if(NIGHT_CASE==5){void*before=parent;change(25);REQUIRE(parent==before&&manager[7]==25,108);snap(5);}
 if(NIGHT_CASE==7)((uint8_t*)parent)[28]=1;
 change(29);REQUIRE(manager[7]==29&&((uint8_t*)manager)[76]==1,109);snap(1);
 if(NIGHT_CASE==3)clear();draw();snap(2);
 if(NIGHT_CASE==0||NIGHT_CASE==2||NIGHT_CASE==3||NIGHT_CASE==6)match();
 if(NIGHT_CASE==6){
  for(unsigned k=0;k<32;k++){
   change(25);struct mercury*m=new_mercury(k+1);append(parent,m);global_frame=k;m->dirty=1;draw();snap(100+k);
   for(unsigned i=0;i<1024;i++)REQUIRE(fb[i]==frames[k*1024+i],110);
   change(29);draw();match();snap(200+k);
  }
 }
 destroy(parent,1);parent=0;snap(3);event(9,*(uint32_t*)0xc03404ac,cleanups,deletes,0);return 0;
}
