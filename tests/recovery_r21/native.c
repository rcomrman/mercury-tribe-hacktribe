/* Laboratory execution of the already existing three-slot renderer only. */
#include <stdint.h>
#include "../recovery_r2/sys.h"
extern const uint8_t original[];
#define CALL(a,t) ((t)(uintptr_t)(a))
static uint32_t calls[3];
struct component { uint32_t *vtable; uint32_t index; };
struct manager { uint8_t pad[0x34]; struct component *slot[3]; };
static void draw(struct component *c){calls[c->index]++;}
static uint32_t vt[3]={(uintptr_t)draw,(uintptr_t)draw,(uintptr_t)draw};
static struct component components[3]={{vt,0},{vt,1},{vt,2}};
static struct manager manager;
static void out(const void*p,unsigned n){sys(4,1,(uintptr_t)p,n,0,0,0);}
int main(void){
 if(sys(192,0xc0000000,0x200000,3,0x32,-1,0)!=0xc0000000)return 70;
 for(unsigned i=0;i<0x200000;i++)((uint8_t*)0xc0000000)[i]=original[i];
 if(sys(125,0xc0000000,0x200000,5,0,0,0))return 71;
 sys(0xf0002,0xc0000000,0xc0200000,0,0,0,0);
 manager.slot[0]=&components[0];manager.slot[1]=&components[1];manager.slot[2]=&components[2];
 CALL(0xc006ea10,void(*)(void*))(&manager);
 uint32_t record[16]={0x5232314e,0x21,calls[0],calls[1],calls[2],sizeof(manager),sizeof(components),0};
 out(record,sizeof(record));return calls[0]==1&&calls[1]==1&&calls[2]==1?0:72;
}
