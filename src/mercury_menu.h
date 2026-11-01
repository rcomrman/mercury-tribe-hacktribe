#ifndef MERCURY_MENU_H
#define MERCURY_MENU_H
#include <stdint.h>
#include "mercury_keys.h"
/* Native, legible, no anti-alias, 128x64 monochrome menu. */
void mercury_menu_render(const md_ui *ui,uint8_t fb[1024]);
#endif
