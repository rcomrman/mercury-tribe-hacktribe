#include "mercury_menu.h"
#include <stdint.h>
/* 5x7 glyphs: 7 rows of 5 bits, printable monochrome. */
typedef struct {char c;uint8_t r[7];} glyph;
static const glyph letters[]={
 {' ',{0,0,0,0,0,0,0}}, {'A',{14,17,17,31,17,17,17}},
 {'B',{30,17,17,30,17,17,30}}, {'C',{14,17,16,16,16,17,14}},
 {'D',{30,17,17,17,17,17,30}}, {'E',{31,16,16,30,16,16,31}},
 {'F',{31,16,16,30,16,16,16}}, {'G',{14,17,16,23,17,17,15}},
 {'H',{17,17,17,31,17,17,17}}, {'I',{31,4,4,4,4,4,31}},
 {'J',{7,2,2,2,18,18,12}}, {'K',{17,18,20,24,20,18,17}},
 {'L',{16,16,16,16,16,16,31}}, {'M',{17,27,21,21,17,17,17}},
 {'N',{17,25,21,19,17,17,17}}, {'O',{14,17,17,17,17,17,14}},
 {'P',{30,17,17,30,16,16,16}}, {'Q',{14,17,17,17,21,18,13}},
 {'R',{30,17,17,30,20,18,17}}, {'S',{15,16,16,14,1,1,30}},
 {'T',{31,4,4,4,4,4,4}}, {'U',{17,17,17,17,17,17,14}},
 {'V',{17,17,17,17,17,10,4}}, {'W',{17,17,17,21,21,21,10}},
 {'X',{17,17,10,4,10,17,17}}, {'Y',{17,17,10,4,4,4,4}},
 {'Z',{31,1,2,4,8,16,31}}, {'0',{14,17,19,21,25,17,14}},
 {'1',{4,12,4,4,4,4,14}}, {'2',{14,17,1,2,4,8,31}},
 {'3',{30,1,1,14,1,1,30}}, {'4',{2,6,10,18,31,2,2}},
 {'5',{31,16,16,30,1,1,30}}, {'6',{14,16,16,30,17,17,14}},
 {'7',{31,1,2,4,8,8,8}}, {'8',{14,17,17,14,17,17,14}},
 {'9',{14,17,17,15,1,1,14}},
 {'/',{1,1,2,4,8,16,16}}, {'-',{0,0,0,31,0,0,0}},
 {'+',{0,4,4,31,4,4,0}}, {':',{0,4,0,0,4,0,0}},
 {'>',{16,8,4,2,4,8,16}}, {'*',{0,10,4,31,4,10,0}},
 {'?',{14,17,1,2,4,0,4}}, {'=',{0,31,0,31,0,0,0}}
};
static void pix(uint8_t *fb,int x,int y,int v){
 if((unsigned)x>=128u||(unsigned)y>=64u)return;
 unsigned off=(unsigned)(y/8)*128u+(unsigned)x;
 unsigned b=1u<<(y%8);
 if(v)fb[off]|=(uint8_t)b;else fb[off]&=(uint8_t)~b;
}
static void rect(uint8_t *fb,int x0,int y0,int x1,int y1,int color){
 for(int y=y0;y<y1;y++)for(int x=x0;x<x1;x++)pix(fb,x,y,color);
}
static const uint8_t *find(char c){
 for(unsigned i=0;i<sizeof(letters)/sizeof(letters[0]);i++)
  if(letters[i].c==c)return letters[i].r;
 return letters[sizeof(letters)/sizeof(letters[0])-1].r;
}
static void txt(uint8_t *fb,int x,int y,const char *s,int white){
 for(int i=0;s[i]&&x<124;i++,x+=6){
   const uint8_t *r=find(s[i]);
   for(int ry=0;ry<7;ry++)for(int rx=0;rx<5;rx++)
    if(r[ry]&(1u<<(4-rx)))pix(fb,x+rx,y+ry,white);
 }
}
static void int_str(int v,char out[7]){
 if(v>99999)v=99999;
 if(v<0)v=0;
 int i=0;char reverse[7];
 do{reverse[i++]=(char)('0'+v%10);v/=10;}while(v&&i<6);
 for(int j=0;j<i;j++)out[j]=reverse[i-1-j];
 out[i]=0;
}
static const char *titles[4]={"AMBIANCE","MOUVEMENT","GLITCH","PISTES"};
static const char *labels[4][4]={
 {"PRESET","INTENSITE","CORDES","REACTION"},
 {"RATE","FLUIDITE","ONDULATION","CHAOS"},
 {"GLITCH","COULURE","PERTE DATA","IMAGE FIGEE"},
 {"IMPACT","SENSIBILITE","CORDE","ROLE"}
};
static const char *preset[8]={"FLOW","SILK","HYPNOSE","ACID","HARD TEK","LOFI","JUNGLE","COLLAPSE"};
static const char *rate[6]={"1/1","1/2","1/4","1/8","1/16","1/32"};
static const char *roles[6]={"KICK","PERC","BASS","MELO","PAD","FX"};
static void value_str(const md_ui *ui,int row,char out[18]){
 int page=ui->page;int v=page==3?ui->tracks[ui->selected_part][row]:ui->global[page*4+row];
 const char *label=0;
 if(page==0&&row==0)label=preset[v<8?v:0];
 if(page==1&&row==0)label=rate[v<6?v:3];
 if(page==3&&row==3)label=roles[v<6?v:0];
 if(page==3&&row==2&&v==0)label="OFF";
 if(label){unsigned j=0;while(label[j]&&j<16){out[j]=label[j];j++;}out[j]=0;return;}
 if(page==3&&row==2){out[0]='C';int_str(v,out+1);return;}
 int_str(v,out);
}
void mercury_menu_render(const md_ui *ui,uint8_t fb[1024]){
 if(!ui||!fb)return;
 for(unsigned i=0;i<1024;i++)fb[i]=0;
 if(ui->screen==MD_LFO_RESERVED){
  const mini_lfo_slot *l=&ui->lfo.slot[ui->selected_lfo<4u?ui->selected_lfo:0u];
  static const char *waves[6]={"SINE","TRI","SAW","SQUARE","S+H","SMOOTH"};
  static const char *fields[7]={"LFO","TRACK","WAVE","RATE","DEPTH","DEST","ENABLED"};
  txt(fb,2,1,"MOD / MINI LFO",1);
  txt(fb,106,1,"L",1);
  char n[7];int_str(ui->selected_lfo+1,n);txt(fb,112,1,n,1);
  rect(fb,0,10,128,11,1);
  txt(fb,2,14,"PARAM",1);txt(fb,80,14,"VALUE",1);
  const uint8_t current=ui->lfo_field%7u;
  txt(fb,2,26,fields[current],1);
  if(current==0)int_str(ui->selected_lfo+1,n);
  if(current==1)int_str(l->track+1,n);
  if(current==2){txt(fb,78,26,waves[l->wave<6?l->wave:0],1);}
  if(current==3){static const char *rates[6]={"1/1","1/2","1/4","1/8","1/16","1/32"};txt(fb,78,26,rates[l->rate<6?l->rate:2],1);}
  if(current==4)int_str(l->depth,n);
  if(current==5)txt(fb,78,26,l->destination==0?"CUTOFF":"RESON",1);
  if(current==6)txt(fb,78,26,l->enabled?"ON":"OFF",1);
  if(current==0||current==1||current==4)txt(fb,79,26,n,1);
  rect(fb,0,40,128,41,1);
  txt(fb,2,44,"LPF- HPF+ BPF NEXT",1);
  txt(fb,2,55,"SHIFT + / - FAST",1);
  return;
 }
 int page=ui->page<4?ui->page:0;
 txt(fb,2,1,titles[page],1);
 if(page==3){
    char number[7];int_str(ui->selected_part+1,number);
    txt(fb,98,1,"P",1);txt(fb,104,1,number,1);
 }else txt(fb,90,1,"GLOBAL",1);
 rect(fb,0,10,128,11,1);
 for(int row=0;row<4;row++){
   int y=13+row*11;
   int selected=row==ui->row;
   int inv=selected&&ui->edit;
   if(inv)rect(fb,0,y-1,128,y+9,1);
   else if(selected)txt(fb,1,y,">",1);
   char result[18];value_str(ui,row,result);
   txt(fb,selected?8:7,y,labels[page][row],inv?0:1);
   int len=0;while(result[len])len++;
   int x=126-len*6;if(x<78)x=78;
   txt(fb,x,y,result,inv?0:1);
 }
 rect(fb,0,57,128,58,1);
 txt(fb,2,58,ui->edit?"LPF - HPF + BPF OK":"LPF HPF BPF EDIT",1);
}
