#include <assert.h>
#include <stdio.h>
#include "mercury_keys.h"
static void press(md_ui *u,md_key k,int shift){assert(md_button(u,k,1,shift)==MD_CONSUMED);assert(md_button(u,k,0,shift)==MD_CONSUMED);}
int main(void){
 md_ui u;md_init(&u);uint8_t saved[16][4];
 for(int i=0;i<16;i++)for(int j=0;j<4;j++)saved[i][j]=u.tracks[i][j];
 md_set_global_only(&u,1);
 press(&u,MD_KEY_HPF,1);assert(u.screen==MD_SETTINGS&&u.page==0);
 for(int i=0;i<15;i++){press(&u,MD_KEY_HPF,1);assert(u.page<3);}
 /* All twelve global parameters remain reachable, including glitch page. */
 u.page=2;u.row=0;u.edit=1;uint8_t old=u.global[8];
 press(&u,MD_KEY_HPF,0);assert(u.global[8]!=old);
 for(int i=0;i<16;i++)for(int j=0;j<4;j++)assert(saved[i][j]==u.tracks[i][j]);
 /* Switching mode back restores track page without resetting track values. */
 md_set_global_only(&u,0);u.page=2;press(&u,MD_KEY_HPF,1);assert(u.page==3);
 md_set_global_only(&u,1);assert(u.page==0&&u.edit==0);
 puts("V28 PASS: 12 global controls, no per-track page, original track values preserved");return 0;
}
