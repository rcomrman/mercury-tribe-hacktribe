#include "mercury_live.h"
#include "sine_q7.h"
/* Native ARMv5TE fixed-point renderer. Every output pixel is generated fresh.
   No frames read from SD. All motion derives from an ABSOLUTE music clock,
   with distinct slow interacting phases, never a short looping film strip.
   Renderer only: no hardware pointers or DSP/audio code. */
static int clamp(int v,int lo,int hi){return v<lo?lo:(v>hi?hi:v);}
static int sn(int p){return rv30_sin[(unsigned)p&255u];}
static uint32_t hash(uint32_t x){x^=x>>16;x*=0x7feb352du;x^=x>>15;x*=0x846ca68bu;return x^(x>>16);}
static void put(uint8_t *a,int x,int y,int val){
 if((unsigned)x>=128u||(unsigned)y>=64u)return;
 unsigned idx=((unsigned)y>>3u)*128u+(unsigned)x;
 uint8_t mask=(uint8_t)(1u<<((unsigned)y&7u));
 if(val)a[idx]|=mask;else a[idx]&=(uint8_t)~mask;
}
static int get(const uint8_t *a,int x,int y){
 if((unsigned)x>=128u||(unsigned)y>=64u)return 0;
 return ((a[((unsigned)y>>3)*128u+(unsigned)x]>>((unsigned)y&7u))&1u);
}
static void span(uint8_t *a,int x,int y0,int y1,int white,int opacity,unsigned salt){
 if((unsigned)x>=128u)return;
 y0=clamp(y0,0,63);y1=clamp(y1,0,63);
 if(y1<y0)return;
 if(opacity>=251){for(int y=y0;y<=y1;y++)put(a,x,y,white);return;}
 for(int y=y0;y<=y1;y++)if((hash((unsigned)(x*13+y*23)+salt)&255u)<(unsigned)opacity)
  put(a,x,y,white);
}
/* Texture evolves by interpolation across MULTIPLE bars, not frame stepping.
   1 cell = 384 ticks = 4 bars @ 24 PPQN; smooth endpoints are continuous. */
static int drift(uint32_t tickq8,unsigned salt){
 uint32_t cell=tickq8/(384u<<8);
 uint32_t f=(tickq8%(384u<<8))>>8;
 int a=(int)(hash(cell+salt)&255u)-128;
 int b=(int)(hash(cell+1u+salt)&255u)-128;
 uint32_t q=f*256u/384u;
 uint32_t ease=q*q*(768u-2u*q)>>16; /* 0..256 cubic smoothstep */
 return a+((b-a)*(int)ease>>8);
}
static int scene_width[8]={78,53,69,63,70,54,62,74};
static int scene_waves[8]={72,48,84,90,65,34,95,79};
static int scene_folds[8]={60,34,93,88,71,28,80,77};
/* 128x64, packed bit order byte=(y>>3)*128+x. */
void md_live_render(const md_music_visual *m,const md_live_settings *s,
                    uint32_t tickq8,uint8_t fb[MD_LCD_BYTES]){
 if(!m||!s||!fb)return;
 for(unsigned i=0;i<MD_LCD_BYTES;i++)fb[i]=0;
 int count=clamp(s->cords,1,8);
 if(count>m->cord_count)count=m->cord_count;
 const int sc=clamp(s->scene,0,7);
 const int fluidity=clamp(s->fluidity,0,100);
 const int wav=clamp((s->waves*(scene_waves[sc]+28))/100,0,125);
 const int folds=clamp((scene_folds[sc]+(int)s->fold)/2,12,100);
 const int thick0=clamp((s->width+scene_width[sc])/25,3,11);
 /* Three phases: common beat-locked movement, long-period drift and
    secondary noncommensurate flows. No loop reset at the end of a bar. */
 uint32_t tr=tickq8;
 if(fluidity<20)tr&=~8191u;      /* 32 ticks = deliberately jerky */
 else if(fluidity<40)tr&=~2047u;
 else if(fluidity<60)tr&=~511u;
 int pFast=(int)((unsigned)m->phase_q16>>8);
 if(fluidity<20)pFast=(pFast/24)*24;
 else if(fluidity<40)pFast=(pFast/12)*12;
 else if(fluidity<60)pFast=(pFast/5)*5; /* exactly one RATE cycle */
 int pSlow=(int)((tr*3u)>>12);  /* about 1 cycle / 15 beats */
 int pDeep=(int)((tr*5u)>>15);  /* about 1 cycle / 68 beats */
 int amorph=drift(tr,0x9411u);
 for(int c=count-1;c>=0;c--){
  int alpha=m->opacity[c];if(alpha<=1)continue;
  int energy=m->energy[c];
  int pitch=(int)m->cord_note[c]-60;
  int role=m->cord_role[c];
  int sep=count<=2?10:count<=4?7:count<=6?5:4;
  int baseline=32+(2*c-count+1)*sep/2;
  /* World coordinate functions are continuously changing; independent
     phases prevent equal-looking, stacked parallel sine curves. */
  unsigned salt=(unsigned)c*0x98511u+(unsigned)sc*0x5143u;
  int phase0=pFast+c*81+amorph/5;
  int phase1=pSlow+c*43+drift(tr,salt+19u)/3;
  int phase2=pDeep+c*107;
  int nibbles=s->chaos;
  for(int x=0;x<128;x++){
   /* Moving domain warp: the ribbon folds around its own wave crests, rather
      than tracing a fixed sine line across every bar. Everything stays live. */
   int xwarp=x+(sn(x*3+phase2+41*c)*wav)/550
              +(sn(x*2+phase1+c*37)*(int)s->swirl)/570
              +(sn(x+phase1+11*c)*folds)/460;
   int arch=sn(xwarp*2+phase0), fold=sn(xwarp*4-phase1+71*c);
   int curl=sn(xwarp*9+phase2+113*c), shear=sn(xwarp+phase1+39*c);
   int edgemask=128; /* subtle emphasis near center */
   if(x<20)edgemask=70+x*3;
   else if(x>108)edgemask=70+(127-x)*3;
   int middle=baseline+arch*wav*edgemask/110000;
   middle+=(fold*folds*edgemask)/130000;
   middle+=(curl*wav)/3300+(shear*wav)/3100;
   middle+=(sn(x*5+phase0+c*47)*(int)s->swirl)/1900;
   middle+=drift(tr,salt+112u)/23;
   if(role==2||role==3)middle+=pitch*energy/1700;
   if(role==4)middle+=sn(x*4+phase1)*energy/1800;
   /* Notes have a clear but bounded bulge. */
   middle+=(sn(x*5+phase0+11*c)*energy)/1100;
   if(nibbles){
    uint32_t block=(unsigned)(x/6)+(tr>>14)*211u+salt;
    int r=(int)(hash(block)&255u)-128;
    middle+=r*nibbles/2500;
   }
   /* Continuous asymmetric swelling: thickness itself belongs to the groove. */
   int taper=88+(sn(xwarp*3-phase0+72*c)*25)/127;
   taper+=(sn(xwarp*7+phase1+26*c)*13)/127;
   taper+=drift(tr,salt+228u)/16;
   int half=(thick0*taper)/100+(energy*m->intensity/15000);
   half+=(sn(pSlow+x*2+c*23)*(int)s->breath)/3500;
   half=clamp(half,2,13);
   /* Grain allows mute dissolve to be gradual with no hard cut. */
   unsigned local_salt=(unsigned)c*943u+((tr>>12)&0xffffu)*11u;
   span(fb,x,middle-half,middle+half,1,alpha,local_salt);
   if(half>=3){
    /* Black chrome slot, with travelling position and occasional split. */
    int hole=clamp((half*(20+(int)s->carve))/155,1,5);
    int slot=middle+(sn(x*6-phase1+43*c)*half)/245;
    span(fb,x,slot-hole,slot+hole-1,0,alpha,local_salt+6u);
    if(s->reflect>18 && s->shine>10){
     int glint=(sn(x*4+phase0/2+c*23)>32)?1:0;
     if(glint && s->rims>25)put(fb,x,middle-half+1,1);
     if(s->reflect>54&&sn(x*8+phase1/2+c*29)>46)
       put(fb,x,slot-hole-2,1);
     if(s->reflect>78&&s->cut>40&&sn(x*5+phase2+c*77)>80)
       put(fb,x,middle+half-2,0);
    }
    /* Satellite filaments are themselves musical and moving, not static. */
    if(folds>38 && x>12 && x<119 && sn(x*3+phase2+c*42)>-25){
      int finger=middle-half-3-(sn(x*5+phase1+c*31)*3)/127;
      if(((x+phase1/7+c*9)&3)==0 && (hash((unsigned)x+salt)&255u)<(unsigned)alpha)
       put(fb,x,finger,1);
    }
    if(s->drips>8 && (x+13*c)%37==4){
      int len=2+(s->drips*3)/20;
      int oscill=(sn(pSlow+x*2+c*39)*3)/127;
      for(int d=0;d<len;d++)if((hash((unsigned)(x*47+d*31)+salt)&255u)<(unsigned)alpha)
       put(fb,x+oscill,middle+half+d+1,1);
    }
   }
  }
 }
 /* Sparking and fracture stay tied to musical energy, not permanently active. */
 if(s->fracture>0){
  for(unsigned c=0;c<(unsigned)count;c++)if(m->energy[c]>110){
   for(unsigned i=0;i<(unsigned)(s->fracture/12u);i++){
    int x=(int)(hash(i*51u+c*71u+(tr>>12))&127u);
    int y=(int)(hash(i*87u+c*43u+(tr>>11))&63u);
    for(int dx=0;dx<3;dx++)put(fb,x+dx,y+(int)(i&1u),0);
   }
  }
 }
 /* A few light fragments can emerge from the moving metallic contour. */
 if(s->reflect>80){
   for(unsigned i=0;i<12;i++){
     int x=(int)(hash(i*187u+(tr>>10))&127u);
     int y=(int)(hash(i*841u+(tr>>11))&63u);
     if(get(fb,x,y))put(fb,x+2,y-1,1);
   }
 }
}
