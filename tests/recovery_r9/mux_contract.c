/* Existing host mux, logical transport only: never an instrument LCD model. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "lcd_source_mux.h"
static unsigned calls;
static uint8_t live[1024],logical_display[1024];
static int outcome,mutate;
static int transmit(void*ctx,unsigned page,const uint8_t bytes[128]){
 (void)ctx;calls++;
 if(!outcome)return 0;
 memcpy(logical_display+128*page,bytes,128);
 if(mutate)live[128*page]=0xee;
 return 1;
}
int main(void){
 lcd_source_mux mux;uint8_t native[1024]={0},initial[1024]={0},snapshot[1024]={0};
 live[0]=0x11;mux_init(&mux,native,live,initial);mux_select(&mux,MUX_VISUAL);
 outcome=0;assert(mux_service_bounded(&mux,0,1,transmit,0)==0);
 assert(calls==1&&mux.shadow[0]==0&&mux.failed_pages==1);
 outcome=1;mutate=1;assert(mux_service_bounded(&mux,0,1,transmit,0)==1);
 assert(logical_display[0]==0x11&&mux.shadow[0]==0xee&&live[0]==0xee);
 unsigned before=calls;assert(mux_service(&mux,0,transmit,0)==0&&calls==before);
 puts("PASS negative: mutable callback source can advance software shadow beyond logical sent bytes");
 memset(logical_display,0,sizeof logical_display);live[0]=0x11;snapshot[0]=0x11;
 mux_init(&mux,native,snapshot,initial);mux_select(&mux,MUX_VISUAL);
 assert(mux_service_bounded(&mux,0,1,transmit,0)==1);
 assert(live[0]==0xee&&snapshot[0]==0x11&&mux.shadow[0]==0x11&&logical_display[0]==0x11);
 puts("PASS positive: frozen snapshot preserves source/committed-shadow/logical-send equality");
 return 0;
}
