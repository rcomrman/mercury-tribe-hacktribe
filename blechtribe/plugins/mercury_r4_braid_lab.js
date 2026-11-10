// Mercury Dust / BLECHTRIBE — V30 Groove experimental portable application.
// Native BLECHTRIBE integer-only JavaScript subset; no DSP/sample/firmware writes.
// Reference: reference/Mercury_Dust_V30_Groove_CORRIGE_Reference.html.
// R4: V30-inspired interwoven liquid strands, page-packed 32x64 tiles. NOT exact V30! No hardware safety certification.
korg.app("Mercury R4", "TOOLS");

// V30 global settings: three pages of four controls, 0-100 except exceptions.
// [PRESET, INTENSITY, CORDS, REACTION, RATE, SMOOTH, WAVE, CHAOS,
//  GLITCH, MELT, DATA LOSS, FRAME SLIP]
const v = [0, 70, 2, 60, 3, 74, 76, 12, 15, 24, 0, 0];
let opened = 0;
let menuOpen = 0;
let page = 0;
let choice = 0;
let phase = 0;
let frames = 0;
let stepPos = 0;
let energy = 0;
let knobReact = 40;
let flash = 0;
// Fixed-point 256-entry sine wave adapted from the previous native sine_q7.h.
// Unsigned bytes keep the packed constant pool economical for the BLECH VM.
const SINE = [
  128,131,134,137,140,144,147,150,153,156,159,162,165,168,171,174,
  177,179,182,185,188,191,193,196,199,201,204,206,209,211,213,216,
  218,220,222,224,226,228,230,232,234,235,237,239,240,241,243,244,
  245,246,248,249,250,250,251,252,253,253,254,254,254,255,255,255,
  255,255,255,255,254,254,254,253,253,252,251,250,250,249,248,246,
  245,244,243,241,240,239,237,235,234,232,230,228,226,224,222,220,
  218,216,213,211,209,206,204,201,199,196,193,191,188,185,182,179,
  177,174,171,168,165,162,159,156,153,150,147,144,140,137,134,131,
  128,125,122,119,116,112,109,106,103,100,97,94,91,88,85,82,
  79,77,74,71,68,65,63,60,57,55,52,50,47,45,43,40,
  38,36,34,32,30,28,26,24,22,21,19,17,16,15,13,12,
  11,10,8,7,6,6,5,4,3,3,2,2,2,1,1,1,
  1,1,1,1,2,2,2,3,3,4,5,6,6,7,8,10,
  11,12,13,15,16,17,19,21,22,24,26,28,30,32,34,36,
  38,40,43,45,47,50,52,55,57,60,63,65,68,71,74,77,
  79,82,85,88,91,94,97,100,103,106,109,112,116,119,122,125
];

function clamp(a, lo, hi) {
  if (a < lo) return lo;
  if (a > hi) return hi;
  return a;
}
function wave(p) {
  return SINE[p & 255] - 128;
}
function storeAll() {
  let i = 0;
  while (i < 12) {
    korg.store.set(i, v[i]);
    i += 1;
  }
  korg.store.save();
}
function drawMenu() {
  if (!opened || !menuOpen) return;
  korg.display.clear();
  korg.display.text("MERCURY V30", 4, 2);
  korg.display.textNumber("PAGE", page + 1, 86, 2);
  let y = 13;
  if (page == 0) {
    korg.display.text("PRESET", 10, y);
    korg.display.text("INTENSITY", 10, y + 11);
    korg.display.text("CORDS", 10, y + 22);
    korg.display.text("REACTION", 10, y + 33);
  }
  if (page == 1) {
    korg.display.text("RATE", 10, y);
    korg.display.text("SMOOTH", 10, y + 11);
    korg.display.text("WAVE", 10, y + 22);
    korg.display.text("CHAOS", 10, y + 33);
  }
  if (page == 2) {
    korg.display.text("GLITCH", 10, y);
    korg.display.text("MELT", 10, y + 11);
    korg.display.text("DATA LOSS", 10, y + 22);
    korg.display.text("FRAME SLIP", 10, y + 33);
  }
  let i = 0;
  while (i < 4) {
    korg.display.number(v[page * 4 + i], 99, y + i * 11);
    i += 1;
  }
  korg.display.text(">", 1, y + choice * 11);
  korg.display.text("MENU: BACK", 4, 56);
}
function adjust(delta) {
  let index = page * 4 + choice;
  let lo = 0;
  let hi = 100;
  if (index == 0) hi = 7;
  if (index == 2) { lo = 1; hi = 8; }
  if (index == 4) hi = 5;
  v[index] = clamp(v[index] + delta, lo, hi);
  drawMenu();
}


const FB = new Array(256);
let sweepX = 0;
// Two primitive spans per tube: white liquid and a carved, following black river.
// Each draw call targets a 32x64 tile; 2-pixel columns avoid full-frame raster costs.
function ink(x, y0, y1, on) {
  y0 = clamp(y0, 0, 63);
  y1 = clamp(y1, 0, 63);
  if (y1 < y0) return;
  let pg = y0 >> 3;
  let end = y1 >> 3;
  while (pg <= end) {
    let low = pg == (y0 >> 3) ? (y0 & 7) : 0;
    let high = pg == end ? (y1 & 7) : 7;
    let mask = (255 << low) & (255 >> (7 - high));
    let at = pg * 32 + x - sweepX;
    if (on) {
      FB[at] |= mask;
      FB[at + 1] |= mask;
      FB[at + 2] |= mask;
      FB[at + 3] |= mask;
    } else {
      FB[at] &= ~mask;
      FB[at + 1] &= ~mask;
      FB[at + 2] &= ~mask;
      FB[at + 3] &= ~mask;
    }
    pg += 1;
  }
}
function drawMatter() {
  if (!opened || menuOpen) return;
  let scene = v[0];
  let p = phase;
  if (v[5] < 20) p = (p / 16) * 16;
  let accent = (energy * v[3]) / 100;
  let base = clamp(4 + v[1] / 21, 3, 10);
  // The envelope swells slowly and falls back when a step/pad injects energy.
  let breath = (wave(p / 3 + scene * 31) * (v[1] + 20)) / 2600;
  // Precompute phases once per tile: unlike R3, the two strands weave in opposition.
  let slowPhase = p / 3 + scene * 27;
  let foldPhase = p / 2 + scene * 13;
  let x = sweepX;
  while (x < sweepX + 32) {
    // Local clearing: four-byte-wide samples in a page-packed tile.
    let band = 0;
    while (band < 8) {
      let at = band * 32 + x - sweepX;
      FB[at] = 0;
      FB[at + 1] = 0;
      FB[at + 2] = 0;
      FB[at + 3] = 0;
      band += 1;
    }
    // Spatial frequencies come from the V30 buildRibbon spirit:
    // a broad undulation, a counter-flowing fold, and a fine curl.
    let broad = wave(x * 2 + slowPhase);
    let fold = wave(x * 5 - foldPhase);
    let curl = wave(x * 9 + slowPhase / 2 + 61);
    let taper = 100;
    if (x < 20) taper = 30 + x * 3;
    if (x > 108) taper = 30 + (127 - x) * 3;
    let bulge = (fold + 128) / 65;
    let thickA = clamp(((base + bulge + breath + accent / 28) * taper) / 100, 1, 15);
    let thickB = clamp(((base - 1 + (curl + 128) / 100) * taper) / 100, 1, 10);
    if (scene == 1 || scene == 5) { thickA -= 1; thickB -= 1; }
    if (scene == 4 || scene == 7) thickA += 2;
    thickA = clamp(thickA, 1, 15);
    thickB = clamp(thickB, 1, 10);

    // Strands braid; they are deliberately NOT two parallel sine strips.
    let middleA = 30 + broad * (8 + v[6] / 12) / 128 + fold / 27 + curl / 47;
    middleA += accent * broad / 1500;
    let middleB = 34 - broad * (7 + v[6] / 15) / 128 + fold / 24 - curl / 38;

    // Draw smaller background strand and carve its own moving black cavity.
    if (v[2] > 1 && scene != 1) {
      ink(x, middleB - thickB, middleB + thickB, 1);
      ink(x, middleB - 1 - curl / 70, middleB + 1 - curl / 70, 0);
    }
    // The large, irregular chrome fold overlays the other ribbon at crossings.
    ink(x, middleA - thickA, middleA + thickA, 1);
    let river = middleA + fold / 30;
    ink(x, river - 2 - v[9] / 60, river + 2 + v[9] / 60, 0);
    // Specular glints are embedded in the liquid, moving with its folds.
    if (((x + p / 8) & 31) == 0) ink(x, middleA - thickA + 2, middleA - thickA + 2, 1);
    x += 4;
  }
  korg.display.clearRect(sweepX, 0, 32, 64);
  korg.display.bitmap(FB, sweepX, 0, 32);
  korg.display.number(scene + 1, 120, 55);
  sweepX = (sweepX + 32) & 127;
}

korg.onEvent("ready", () => {
  let i = 0;
  while (i < 12) {
    let n = korg.store.get(i, v[i]);
    if (i == 0) n = clamp(n, 0, 7);
    else if (i == 2) n = clamp(n, 1, 8);
    else if (i == 4) n = clamp(n, 0, 5);
    else n = clamp(n, 0, 100);
    v[i] = n;
    i += 1;
  }
});
korg.onEvent("open", () => {
  opened = 1;
  menuOpen = 0;
  frames = 0;
  phase = 0;
  sweepX = 0;
  drawMatter();
});
korg.onEvent("close", () => {
  if (opened) storeAll();
  opened = 0;
  menuOpen = 0;
});
korg.onEvent("buttonPress", (key) => {
  if (!opened) return;
  if (key == korg.key.MENU) {
    menuOpen = 1 - menuOpen;
    if (menuOpen) drawMenu();
    else { storeAll(); korg.display.clear(); sweepX = 0; drawMatter(); }
    return;
  }
  if (menuOpen) {
    if (key == korg.key.EDIT_LEFT) page = (page + 2) % 3;
    if (key == korg.key.EDIT_RIGHT) page = (page + 1) % 3;
    if (key == korg.key.PART_LEFT) choice = (choice + 3) % 4;
    if (key == korg.key.PART_RIGHT) choice = (choice + 1) % 4;
    if (key == korg.key.BAR_1) { adjust(-1); return; }
    if (key == korg.key.BAR_2) { adjust(-10); return; }
    if (key == korg.key.BAR_3) { adjust(10); return; }
    if (key == korg.key.BAR_4) { adjust(1); return; }
    drawMenu();
  } else {
    if (key == korg.key.PART_RIGHT) v[0] = (v[0] + 1) % 8;
    if (key == korg.key.PART_LEFT) v[0] = (v[0] + 7) % 8;
    if (key == korg.key.PART_RIGHT || key == korg.key.PART_LEFT) drawMatter();
  }
});
korg.onEvent("pad", (index, down, velocity) => {
  if (!opened || menuOpen || !down) return;
  energy = clamp(velocity, 20, 127);
  flash = 2;
});
korg.onEvent("step", (step) => {
  stepPos = step;
  // Synthetic beat pulse: NOT audio-based kick detection.
  if ((step & 3) == 0) { energy = 96; flash = 2; }
  else if (energy < 30) energy = 30;
});
korg.onEvent("knob", (index, value) => {
  // Read only! OSC EDIT knob still performs its normal Korg audio function.
  if (!opened) return;
  if (index == 9) knobReact = clamp((value * 100) / 255, 0, 100);
});
korg.onEvent("frame", () => {
  if (!opened || menuOpen) return;
  frames += 1;
  if (energy > 0) energy = clamp(energy - 4, 0, 127);
  if (flash > 0) flash -= 1;
  // A full image is completed over four consecutive 40ms frames.
  if (sweepX == 0) phase += (1 + v[4] * 2) + knobReact / 25;
  phase &= 2047;
  if (v[11] > 30 && ((frames + stepPos) % 18) < v[11] / 20) return;
  drawMatter();
});
