#include "md23_panel_gateway.h"
static volatile struct {
 uint32_t magic;
 md17_adapter *app;
 uint8_t armed;
} g_gateway = {.magic=0x4D443233u,.app=0,.armed=0};
static int has_owned_key(const md17_adapter *app){
 const md17_panel *p=&app->panel;
 for(unsigned i=0;i<3;i++)
  if(p->key_down[i] && p->key_owner[i]==MD17_OWNER_MERCURY)return 1;
 return p->exit_down&&p->exit_owner==MD17_OWNER_MERCURY;
}
int md23_panel_pending_mercury_release(void){
 /* If the gateway metadata is damaged, fail closed rather than attempting
  * to reset a potentially still-held Mercury key. */
 if(g_gateway.magic!=0x4D443233u)return 1;
 if(!g_gateway.app)return 0;
 if(!g_gateway.app->initialized)return 1;
 return has_owned_key(g_gateway.app);
}
void md23_panel_attach(md17_adapter *app,uint8_t verified){
 if(!verified||!app||!app->initialized||!app->decoder_verified){
  md23_panel_disarm();return;
 }
 /* The keyboard keymap is configured by the caller. No fake fixed EXIT ID. */
 g_gateway.app=app;g_gateway.armed=1;
}
void md23_panel_disarm(void){
 g_gateway.armed=0;
 if(g_gateway.app){
  md17_panel_enable(&g_gateway.app->panel,0);
  md17_panel_exit(&g_gateway.app->panel);
 }
 /* Keep adapter pointer until pending releases are swallowed. */
}
void md23_panel_forget_untrusted(void){
 g_gateway.armed=0u;
 g_gateway.app=0;
}
int md23_route_key(uint32_t physical_code,uint32_t pressed){
 if(g_gateway.magic!=0x4D443233u || !g_gateway.app)return 0;
 md17_adapter *app=g_gateway.app;
 if(!app->initialized)return 0;
 if(!g_gateway.armed && !has_owned_key(app)){
  g_gateway.app=0;
  return 0;
 }
 if(!g_gateway.armed && pressed){
  /* Do not leak autorepeat of a Mercury-owned key to Korg after disarm. */
  const md17_panel *p=&app->panel;
  for(unsigned i=0;i<3;i++){
   unsigned id=(i==0)?p->map.lpf:(i==1)?p->map.hpf:p->map.bpf;
   if(physical_code==id && p->key_down[i] && p->key_owner[i]==MD17_OWNER_MERCURY)return 1;
  }
  if(physical_code==p->map.exit && p->exit_down && p->exit_owner==MD17_OWNER_MERCURY)return 1;
  return 0;
 }
 /* md17_panel_event is responsible for never leaking a release after
  * consuming its down event, even when EXIT has changed the menu. */
 return md17_on_key(app,physical_code,pressed?1u:0u)==MD17_CONSUME_MERCURY;
}
