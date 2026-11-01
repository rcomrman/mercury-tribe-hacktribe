/* MD44 research-only regression: refused native-return requests cannot be
 * bypassed by a new SHIFT+filter gesture while native handoff is pending. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "md43_platform_port.h"

typedef struct {unsigned frames, native_calls; unsigned decline_native;} fake;
static int offer(void *ctx,const uint8_t frame[1024]){
 fake *f=(fake *)ctx; (void)frame; f->frames++; return 1;
}
static int native(void *ctx){
 fake *f=(fake *)ctx; f->native_calls++;
 if(f->decline_native){f->decline_native--;return 0;}
 return 1;
}
static void shift_bpf(md43_port *p){
 assert(md43_key_event(p,MD43_KEY_SHIFT,1)==0);
 assert(md43_key_event(p,MD43_KEY_BPF,1)==1);
 assert(md43_key_event(p,MD43_KEY_BPF,0)==1);
 assert(md43_key_event(p,MD43_KEY_SHIFT,0)==0);
}
int main(void){
 static md43_port p;
 static fake f;
 uint8_t initial[1024]={0};
 md43_platform_api api={offer,native,&f};
 assert(md43_init(&p,initial,api));
 shift_bpf(&p);
 assert(p.runtime.ui.screen==MD_VISUAL);
 assert(md43_ui_tick(&p,100)==1 && f.frames==1);
 /* EXIT switches software UI to Korg, but a refused request has not
  * transferred native ownership even at the API contract level. */
 assert(md43_key_event(&p,MD43_KEY_EXIT,1)==1);
 assert(md43_key_event(&p,MD43_KEY_EXIT,0)==1);
 assert(p.runtime.ui.screen==MD_KORG);
 f.decline_native=2;
 assert(md43_ui_tick(&p,150)==0);
 assert(p.pending_native_request==1 && f.native_calls==1);
 /* RED on MD43: SHIFT+BPF prematurely enters custom UI. */
 shift_bpf(&p);
 assert(p.runtime.ui.screen==MD_KORG);
 assert(p.pending_native_request==1);
 /* RED on MD43: SHIFT+HPF opens settings before native request succeeds. */
 assert(md43_key_event(&p,MD43_KEY_SHIFT,1)==0);
 assert(md43_key_event(&p,MD43_KEY_HPF,1)==1);
 assert(md43_key_event(&p,MD43_KEY_HPF,0)==1);
 assert(md43_key_event(&p,MD43_KEY_SHIFT,0)==0);
 assert(p.runtime.ui.screen==MD_KORG);
 /* A key down refused while pending stays Mercury-owned on its release,
  * even when the pending request is accepted between the two events. */
 assert(md43_key_event(&p,MD43_KEY_SHIFT,1)==0);
 assert(md43_key_event(&p,MD43_KEY_BPF,1)==1);
 assert(md43_ui_tick(&p,160)==0); /* still declined */
 assert(md43_ui_tick(&p,170)==0); /* now accepted */
 assert(f.native_calls==3 && p.pending_native_request==0);
 assert(md43_key_event(&p,MD43_KEY_BPF,0)==1);
 assert(md43_key_event(&p,MD43_KEY_SHIFT,0)==0);
 assert(p.runtime.ui.screen==MD_KORG);
 shift_bpf(&p);
 assert(p.runtime.ui.screen==MD_VISUAL);
 assert(md43_ui_tick(&p,220)==1);
 puts("MD44 PASS: declined native requests block premature Mercury reentry and preserve key ownership (HOST ONLY).");
 return 0;
}
