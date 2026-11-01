#ifndef MD21_V14_PROFILES_H
#define MD21_V14_PROFILES_H
#include <stdint.h>
#include "md15_bridge.h"
#define MD21_SCENES 8
#define MD21_FX 24
typedef struct {
 const char *name; uint8_t base_scene,cords,rate,data_loss,frame_slip;
 uint8_t fx[MD21_FX];
} md21_v14_profile;
extern const md21_v14_profile md21_v14[MD21_SCENES];
void md21_apply_v14(md15_bridge *b,uint8_t scene);
#endif
