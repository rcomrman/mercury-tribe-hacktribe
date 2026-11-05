/* Local RAM register double, not MMIO and not a hardware-success simulation. */
#include "../recovery_r2/sys.h"
extern const uint8_t original[];
static unsigned fake_registers[32];
static void emit(unsigned stage,unsigned value){unsigned r[4]={0x52323333,CASE,stage,value};sys(4,1,(uintptr_t)r,sizeof(r),0,0,0);}
int main(void){
 if(sys(192,0xc0000000,0x200000,3,0x32,-1,0)!=0xc0000000)return 70;
 for(unsigned i=0;i<0x200000;i++)((uint8_t*)0xc0000000)[i]=original[i];
 if(sys(125,0xc0000000,0x200000,5,0,0,0))return 71;
 sys(0xf0002,0xc0000000,0xc0200000,0,0,0,0);
 fake_registers[4]=CASE==1||CASE==3||CASE==4?0x200:0;
 unsigned (*probe)(void*)=(void*)0xc00117c8;
 void (*waiter)(void*)=(void*)0xc0015cdc;
 emit(0,probe(fake_registers));
 if(CASE==2||CASE==3){waiter(fake_registers);emit(1,0);}
 if(CASE==4){
  static unsigned char data[128];for(unsigned i=0;i<128;i++)data[i]=(unsigned char)i;
  fake_registers[16]=0x80000000u;
  unsigned (*send)(void*,const void*,unsigned,unsigned)=(void*)0xc001851c;
  unsigned result=send(fake_registers,data,128,0);emit(2,result);emit(3,fake_registers[15]);
 }
 return 0;
}
