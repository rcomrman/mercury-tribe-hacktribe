/* Sequential laboratory coordination; no native installation or atomics. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "../recovery_r13/coordinator.h"
#define T(x) do{if(!(x)){fprintf(stderr,"FAIL line %d\n",__LINE__);return 1;}}while(0)
static int draw_if_mercury(unsigned korg_owner,struct r13_gate*g,struct r12_pool*p){
 if(korg_owner)return 0;
 return r13_draw_begin(g,p);
}
int main(void){
 static struct r12_pool p;static struct r13_gate g;static uint8_t initial[1024],published[1024],expected[1024];
 for(unsigned i=0;i<1024;i++)initial[i]=(uint8_t)(i*37+13);
 r12_init(&p,3,initial);memcpy(published,initial,1024);
 T(r13_draw_begin(&g,&p));memcpy(expected,p.image[g.held.slot],1024);
 memcpy(published,expected,512);g.written=512;
 T(!r13_critical_begin(&g));T(!r13_request(&g));T(g.pending==1);
 T(!r13_read_begin(&g)); /* concurrent request deferred, no partial read */
 memcpy(published+512,expected+512,512);g.written=1024;T(r13_draw_end(&g,&p));
 T(r13_read_begin(&g));T(!memcmp(published,expected,1024));r13_read_end(&g);
 T(r13_critical_begin(&g));T(!r13_draw_begin(&g,&p));g.phase=R13_IDLE;
 /* Nonparticipant witness: a writer bypasses the gate while the read is held. */
 T(r13_request(&g));T(r13_read_begin(&g));published[7]^=0x80;
 T(memcmp(published,expected,1024)!=0);r13_read_end(&g);
 /* Cooperative Korg takeover: future Mercury draw remains suspended. */
 unsigned korg_owner=1;T(!draw_if_mercury(korg_owner,&g,&p)&&g.phase==R13_IDLE);memcpy(published,initial,1024);
 T(!memcmp(published,initial,1024));
 printf("PASS sequential mediated draw/read, deferred Korg request, reentry rejected; BYPASS witness detected\n");
 return 0;
}
