#ifndef MD24_VISUAL_SERVICE_H
#define MD24_VISUAL_SERVICE_H
#include "md24_refresh_gate.h"
#include "md18_lcd_abi.h"
/* Application-side LCD scheduling port: doesn't call Korg, doesn't write SPI.
 * Return 1 means the verified *Korg* task should request its own normal
 * display refresh; additionally forces one restore on exit to Korg. */
typedef struct {
 md17_adapter *app;
 md18_lcd_hook *lcd;
 md24_refresh_gate gate;
 uint8_t in_custom_view;
 uint32_t visual_refreshes,korg_restores,unverified_rejections;
} md24_visual_service;
void md24_visual_service_init(md24_visual_service *,md17_adapter *,md18_lcd_hook *);
int md24_visual_service_tick(md24_visual_service *,uint32_t now_ms,
                             uint8_t serialized_korg_lcd_task_verified);
#endif
