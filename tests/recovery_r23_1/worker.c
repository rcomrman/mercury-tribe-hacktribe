/* ARM Linux/QEMU fixture; original worker and comparator, no peripheral emulation. */
#define main r9_unused_main
#define R9_CASE (2300+CASE)
#include "../recovery_r9/lcd.c"
#undef main
static uint8_t mercury[1024];
int main(void){
 init();desc[4]=1;desc[5]=1;desc[12]=0;
 for(unsigned i=0;i<1024;i++)mercury[i]=0xee;
 emit(0,0,0);
 if(CASE==0){worker(0);CHECK(desc[5]==1,210);emit(20,0,0);return 0;}
 if(CASE==1){desc[5]=0;source[401]^=0x80;worker(0);CHECK(source[401]!=shadow[401],211);emit(20,0,0);return 0;}
 if(CASE==2){
  /* Policy is fixture-only: omit the worker call, keep native source/shadow. */
  source[401]^=0x80;emit(10,mercury[0],0);
  CHECK(source[401]!=shadow[401],212);CHECK(compare(3,0)==1,213);
  CHECK(source[401]==shadow[401],214);emit(20,0,0);return 0;
 }
 if(CASE==3){source[401]^=0x80;emit(10,0,0);worker(0);return 215;}
 if(CASE==4){desc[5]=0;desc[12]=1;emit(10,0,0);worker(0);return 216;}
 if(CASE==5){desc[5]=0;source[401]^=0x80;worker(2);CHECK(source[401]!=shadow[401],217);emit(20,0,0);return 0;}
 return 218;
}
