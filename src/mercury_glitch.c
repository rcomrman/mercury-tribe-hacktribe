#include "mercury_glitch.h"
/* Pixel and page order match V10's C compositor. */
static unsigned bit_get(const uint8_t *b, unsigned x,unsigned y) {
    if(x>=128u || y>=64u)return 0;
    return (b[(y>>3u)*128u+x]>>(y&7u))&1u;
}
static void bit_put(uint8_t *b,unsigned x,unsigned y,unsigned v) {
    if(x>=128u || y>=64u)return;
    unsigned off=(y>>3u)*128u+x;
    uint8_t mask=(uint8_t)(1u<<(y&7u));
    if(v)b[off]|=mask;else b[off]&=(uint8_t)~mask;
}
static uint32_t mix(uint32_t x) {
    x ^= x>>16; x*=0x7feb352du; x^=x>>15; x*=0x846ca68bu; return x^(x>>16);
}
void md_glitch_init(md_glitch_state *s){
    if(!s)return;
    uint8_t *p=(uint8_t *)s;
    for(unsigned i=0;i<sizeof(*s);i++)p[i]=0;
}
static uint8_t clipped(uint8_t x){return x>100u?100u:x;}
void md_glitch_set(md_glitch_state *s,uint8_t loss,uint8_t slip,uint8_t melt){
    if(!s)return;
    s->data_loss=clipped(loss);
    s->frame_slip=clipped(slip);
    s->melt=clipped(melt);
    if(!loss&&!slip&&!melt)s->ms_remaining=0;
}
void md_glitch_note(md_glitch_state *s,uint8_t vel){
    if(!s || !vel || (!s->data_loss&&!s->frame_slip&&!s->melt))return;
    s->strength=vel>127u?127u:vel;
    s->ms_remaining=(uint16_t)(45u+(uint16_t)s->strength);
    s->event_id++;
}
void md_glitch_tick(md_glitch_state *s,uint16_t elapsed_ms){
    if(!s)return;
    if(elapsed_ms >= s->ms_remaining)s->ms_remaining=0;
    else s->ms_remaining=(uint16_t)(s->ms_remaining-elapsed_ms);
}
void md_glitch_apply(md_glitch_state *s,const uint8_t src[MD_GLITCH_BYTES],uint8_t dst[MD_GLITCH_BYTES]){
    if(!s||!src||!dst)return;
    /* copy before altering, including source/destination alias */
    for(unsigned i=0;i<MD_GLITCH_BYTES;i++)dst[i]=src[i];
    if(s->ms_remaining==0||!s->strength){
        for(unsigned i=0;i<MD_GLITCH_BYTES;i++)s->previous[i]=src[i];
        s->has_previous=1u;
        return;
    }
    uint32_t seed=mix(s->event_id*659u+137u);
    unsigned power=(unsigned)s->strength;  /* event strength remains stable for this impulse */
    if(s->data_loss){
        unsigned bands=1u+(unsigned)s->data_loss/25u;
        for(unsigned i=0;i<bands;i++){
            uint32_t h=mix(seed+0x1327u*i);
            unsigned y=(h>>5)&63u;
            unsigned length=2u+((h>>16)%8u);
            unsigned xmax=24u+((h>>8)%104u);
            unsigned left=(h>>21)%64u;
            if((uint32_t)s->data_loss*power < 700u && i>0)continue;
            for(unsigned yy=y;yy<y+length && yy<64u;yy++)
                for(unsigned x=left;x<xmax && x<128u;x++)bit_put(dst,x,yy,0u);
        }
    }
    if(s->frame_slip && s->has_previous){
        uint32_t h=mix(seed^0x8f226a41u);
        unsigned y=(h>>3)%48u;
        unsigned height=2u+(unsigned)s->frame_slip/12u;
        unsigned shift=1u+(unsigned)s->frame_slip/12u;
        int off=(h&1u)?(int)shift:-(int)shift;
        for(unsigned yy=y; yy<y+height && yy<64u;yy++)
            for(unsigned x=0;x<128u;x++){
                int sx=(int)x+off;
                bit_put(dst,x,yy,sx>=0&&sx<128?bit_get(s->previous,(unsigned)sx,yy):0u);
            }
    }
    if(s->melt && s->has_previous){
        unsigned streaks=1u+s->melt/14u;
        for(unsigned i=0;i<streaks;i++){
            uint32_t h=mix(seed+0xd441u*i);
            unsigned x=(h>>10)&127u;
            unsigned y=(h>>18)%48u;
            unsigned width=1u+((h>>23)&3u);
            unsigned fall=1u+s->melt/8u;
            for(unsigned xx=x;xx<x+width&&xx<128u;xx++){
                for(int yy=63;yy>=(int)y;yy--){
                    int oldY=yy-(int)fall;
                    bit_put(dst,xx,(unsigned)yy,oldY>=(int)y?bit_get(s->previous,xx,(unsigned)oldY):0u);
                }
            }
        }
    }
    /* Freeze the snapshot during the impulse, deliberately. Refresh on recovery. */
}
