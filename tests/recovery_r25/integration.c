/* Linux/QEMU only: Korg image RX, anonymous LCD memory, no peripheral replies. */
#define R9_CASE (2500+2*SCENE+WORKER)
#define main r9_unused_main
#include "../recovery_r9/lcd.c"
#undef main
extern const uint8_t frames[];
int main(void){
 init();const uint8_t *frame=frames+SCENE*4096;
 for(unsigned i=0;i<1024;i++)source[i]=shadow[i]=0;
 desc[4]=1;desc[5]=1;desc[12]=0;
 for(int y=0;y<64;y++)for(int x=0;x<128;x++){
  int v=(frame[(y/8)*128+x]>>(y%8))&1;
  FN(void(*)(int*,int*,int*),0xc0015824)(&x,&y,&v);
 }
 for(unsigned i=0;i<1024;i++)CHECK(source[i]==frame[i],210);
 emit(10,SCENE,WORKER);
 if(WORKER){worker(1);return 211;}
 for(unsigned page=0;page<8;page++){
  CHECK(compare(page,1)==1,212);
  for(unsigned i=0;i<128;i++)CHECK(shadow[page*128+i]==frame[page*128+i],213);
  emit(30+page,1,page);
 }
 CHECK(source[-1]==0x39,214);emit(20,0,0);return 0;
}
