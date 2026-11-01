/* MD42: intentionally reproduces an UNFIXED hardware-ack gap in MD41.
 * This host-only test shows that identical buffer convergence can occur
 * despite failed hypothetical transfer; it is not a successful TX test.
 * Do not use this as a justification to flash firmware.
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "md30_lcd_gate.h"
#include "md31_lcd_comparator.h"
#include "md20_keys.h"

static uint8_t frame[1024],shadow[1024];
static uint32_t ticks=0;
static unsigned attempts=0, failures=0;
static int io_works=0;
static uint32_t get_ticks(void){return ticks;}
static uint32_t dispatch(void *ctx,uint32_t opcode,uint32_t arg){
 (void)ctx;assert(opcode==2 && arg==0);return 0;
}
static uint32_t compare(const uint32_t *page,uint32_t force){
 assert(page && *page<8);
 unsigned off=*page*128;
 int changed=force || memcmp(frame+off,shadow+off,128)!=0;
 memcpy(shadow+off,frame+off,128);
 if(changed){attempts++;if(!io_works)failures++;}
 /* Korg's page-comparator return can say 'changed', but carries no
  * independent SPI success result in the MD41 interface. */
 return changed ? 1u:0u;
}
static void pages(void){
 for(uint32_t p=0;p<8;p++) (void)md31_compare_visit(&p,0);
}
static md17_keymap map(void){
 md17_keymap k={.shift=MD20_KEY_SHIFT,.lpf=MD20_KEY_LPF,
 .hpf=MD20_KEY_HPF,.bpf=MD20_KEY_BPF,.exit=0xfe};return k;
}
static void start(void){
 assert(md30_arm_for_verified_lab(frame,shadow,compare,map(),get_ticks,MD25_REQUIRED_PROOF));
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,1)==0);
 assert(md30_route_decoded_key(MD20_KEY_BPF,1)==1);
 assert(md30_route_decoded_key(MD20_KEY_BPF,0)==1);
 assert(md30_route_decoded_key(MD20_KEY_SHIFT,0)==0);
 ticks+=40;md30_callback_visit();pages();
 md30_disarm();
 assert(md30_status()->pending_native_restore);
 ticks+=40;md30_callback_visit();
 assert(md30_status()->restore_issued);
}
int main(void){
 for(unsigned i=0;i<1024;i++)frame[i]=(uint8_t)(i*11+7);
 md31_host_bind(compare,dispatch);
 start();
 /* Inject an unobservable hardware failure AFTER Korg's comparator
  * has copied pixels to shadow. A real hardware transfer might fail,
  * but MD41 knows only frame==shadow. */
 io_works=0;pages();
 assert(failures>0);
 assert(memcmp(frame,shadow,1024)==0);
 ticks+=40;md30_callback_visit();
 assert(!md30_status()->pending_native_restore);
 assert(md30_arm_for_verified_lab(frame,shadow,compare,map(),get_ticks,MD25_REQUIRED_PROOF));
 printf("MD42 KNOWN GAP REPRODUCED: %u failed modeled sends; "
        "MD41 accepted buffer restoration and rearm without SPI ack (HOST ONLY)\n",failures);
 return 0;
}
