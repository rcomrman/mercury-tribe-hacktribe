#ifndef MD23_PANEL_GATEWAY_H
#define MD23_PANEL_GATEWAY_H
#include <stdint.h>
#include "md17_korg_adapter.h"
/* The ARM veneer calls this *one* route function rather than the old
 * disconnected md20_router, so UI state and key ownership are shared.
 * Default DISARMED until an independently verified startup hook attaches it.
 * EXIT code must be explicitly confirmed on hardware before arming. */
void md23_panel_attach(md17_adapter *app,uint8_t verified);
void md23_panel_disarm(void);
/* A held Mercury-owned key must complete its UP before reinitializing UI state.
 * Use only when md25_state_intact() holds (canaries are not RAM proof). */
int md23_panel_pending_mercury_release(void);
/* Drop the gateway pointer WITHOUT dereferencing a potentially corrupt UI.
 * Last-resort fail-closed fallback; consumed key releases may be lost. */
void md23_panel_forget_untrusted(void);
int md23_route_key(uint32_t physical_code,uint32_t pressed);
#endif
