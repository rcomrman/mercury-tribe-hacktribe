#include "md21_v14_profiles.h"
/* Extracted from the actual V14 JavaScript source. No GIF frames. */
const md21_v14_profile md21_v14[MD21_SCENES] = {
 {"V30 FLOW",0,2,2,0,0,{85, 76, 72, 66, 38, 76, 74, 54, 82, 80, 75, 68, 48, 20, 42, 12, 3, 0, 2, 24, 0, 8, 14, 65}},
 {"SILK",1,1,1,0,0,{85, 57, 42, 36, 22, 52, 90, 66, 62, 96, 90, 65, 26, 14, 37, 21, 0, 0, 0, 44, 0, 0, 34, 86}},
 {"HYPNOSE",2,3,1,0,0,{85, 68, 86, 68, 35, 78, 85, 52, 88, 78, 91, 73, 86, 68, 75, 45, 7, 0, 0, 34, 0, 7, 48, 84}},
 {"ACID",3,3,3,4,4,{85, 58, 96, 89, 79, 89, 34, 45, 86, 93, 96, 70, 82, 69, 58, 20, 40, 21, 18, 61, 20, 28, 21, 59}},
 {"HARD TEK",4,3,4,38,30,{92, 66, 80, 72, 64, 70, 24, 34, 86, 95, 68, 83, 74, 37, 94, 24, 87, 75, 75, 50, 85, 67, 33, 39}},
 {"LOFI DREAM",1,2,1,0,0,{85, 39, 33, 36, 22, 32, 90, 83, 62, 96, 38, 65, 26, 14, 37, 21, 0, 0, 0, 44, 0, 0, 34, 86}},
 {"JUNGLE BREAK",3,5,4,42,35,{85, 32, 96, 89, 79, 89, 34, 11, 86, 93, 96, 70, 82, 69, 58, 20, 40, 21, 18, 61, 86, 28, 21, 59}},
 {"DATA COLLAPSE",4,4,4,92,88,{92, 86, 60, 72, 64, 70, 24, 6, 86, 95, 68, 83, 74, 37, 94, 24, 87, 90, 75, 50, 85, 67, 33, 39}},
};
enum { FX_LENGTH=0,FX_WIDTH,FX_FOLD,FX_STRANDS,FX_FLOW,FX_WAVES,FX_VISCOSITY,FX_DRIPS,
 FX_CARVE,FX_RIMS,FX_SHINE,FX_CUT,FX_SWIRL,FX_ORBIT,FX_BREATH,FX_ECHO,
 FX_GLITCH,FX_TEAR,FX_SHAKE,FX_MELT,FX_FRACTURE,FX_SPARKS,FX_TRAIL,FX_LIFE };
void md21_apply_v14(md15_bridge *b,uint8_t scene){
 if(!b||scene>=MD21_SCENES)return;
 const md21_v14_profile *p=&md21_v14[scene];
 uint8_t intensity=b->music.intensity; /* Switching presets preserves user intensity. */
 b->preset=scene;
 b->render.scene=scene;
 b->music.cord_count=p->cords;b->render.cords=p->cords;
 b->music.rate=p->rate;
 b->render.width=p->fx[FX_WIDTH];
 b->render.waves=p->fx[FX_WAVES];
 b->render.fluidity=p->fx[FX_VISCOSITY];
 b->render.drips=p->fx[FX_DRIPS];
 b->render.reflect=p->fx[FX_SHINE];
 b->render.chaos=(uint8_t)((p->fx[FX_SWIRL]+p->fx[FX_ORBIT])/2u);
 b->render.fold=p->fx[FX_FOLD];
 b->render.swirl=p->fx[FX_SWIRL];
 b->render.breath=p->fx[FX_BREATH];
 b->render.carve=p->fx[FX_CARVE];
 b->render.cut=p->fx[FX_CUT];
 b->render.rims=p->fx[FX_RIMS];
 b->render.shine=p->fx[FX_SHINE];
 b->render.fracture=p->fx[FX_FRACTURE];
 b->render.sparks=p->fx[FX_SPARKS];
 b->render.trail=p->fx[FX_TRAIL];
 uint8_t melt=p->fx[FX_MELT];
 md_glitch_set(&b->glitch,p->data_loss,p->frame_slip,melt);
 b->music.intensity=intensity;
}
