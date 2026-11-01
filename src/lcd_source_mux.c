#include "lcd_source_mux.h"
void mux_init(lcd_source_mux *m,const uint8_t korg[MUX_BYTES],const uint8_t visual[MUX_BYTES],const uint8_t *initial){
 if(!m)return;
 uint8_t *p=(uint8_t*)m;
 for(unsigned i=0;i<sizeof(*m);i++)p[i]=0;
 m->korg=korg;m->visual=visual;m->owner=MUX_KORG;
 if(initial){for(unsigned i=0;i<MUX_BYTES;i++)m->shadow[i]=initial[i];
  for(unsigned i=0;i<MUX_COUNT;i++)m->valid[i]=1;
 }
}
void mux_select(lcd_source_mux *m,mux_owner mode){
 if(m)m->owner=mode==MUX_VISUAL?MUX_VISUAL:MUX_KORG;
}
unsigned mux_service_bounded(lcd_source_mux *m,int force,unsigned max_pages,mux_tx_page send,void *ctx){
 if(!m||!m->korg||!m->visual||!send||max_pages==0)return 0;
 const uint8_t *source=m->owner==MUX_VISUAL?m->visual:m->korg;
 unsigned sent=0,attempted=0;
 /* IMPORTANT: the previous version restarted at page zero on every poll.
    With pages 0/1 constantly dirty and max_pages=2, pages 2..7 starved.
    Rotate the starting page after any attempted transfer, including failures. */
 unsigned start=m->next_page % MUX_COUNT;
 for(unsigned scanned=0;scanned<MUX_COUNT && attempted<max_pages;scanned++){
  unsigned pg=(start+scanned)%MUX_COUNT;
  unsigned off=pg*MUX_PAGE;
  int dirty=force || !m->valid[pg];
  if(!dirty)for(unsigned i=0;i<MUX_PAGE;i++)if(source[off+i]!=m->shadow[off+i]){dirty=1;break;}
  if(!dirty)continue;
  attempted++;
  /* Advance even if the transfer fails. A failed page stays dirty and
     therefore will be retried on subsequent passes. */
  m->next_page=(uint8_t)((pg+1u)%MUX_COUNT);
  if(send(ctx,pg,source+off)){
   for(unsigned i=0;i<MUX_PAGE;i++)m->shadow[off+i]=source[off+i];
   m->valid[pg]=1;sent++;
  }else m->failed_pages++;
 }
 m->dirty_pages+=sent;m->total_refreshes++;
 return sent;
}
unsigned mux_service(lcd_source_mux *m,int force,mux_tx_page send,void *ctx){
 return mux_service_bounded(m,force,MUX_COUNT,send,ctx);
}
