/* Isolated ARM fixture; native code is mapped RX and peripheral MMIO is absent. */
#define main r9_unused_main
#define R9_CASE (2400+CASE)
#include "../recovery_r9/lcd.c"
#undef main
int main(void){
 init();desc[4]=1;desc[5]=0;desc[12]=0;emit(0,0,0);
 if(CASE==0){
  CHECK(command(2,0)==0&&desc[5]==1,210);source[401]^=0x80;emit(10,desc[5],0);
  /* Omitted invocation is a fixture-only suspension, not a firmware hook. */
  CHECK(source[401]!=shadow[401]&&desc[5]==1,211);emit(20,desc[5],0);return 0;
 }
 if(CASE==1){
  for(unsigned i=0;i<4;i++)CHECK(command(2,0)==0,212);
  CHECK(desc[5]==1,213);emit(20,desc[5],4);return 0;
 }
 if(CASE==2){
  source[128+1]^=0x80;source[3*128+2]^=0x80;CHECK(command(2,0)==0,214);emit(10,0,0);
  worker(0);return 215;
 }
 if(CASE==3){
  source[401]^=0x80;CHECK(compare(3,0)==1,216);emit(10,0,0);
  CHECK(compare(3,0)==0,217);emit(20,0,0);return 0;
 }
 return 218;
}
