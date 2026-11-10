// Mercury Dust / BLECHTRIBE — V30 Groove experimental portable application.
// Native BLECHTRIBE integer-only JavaScript subset; no DSP/sample/firmware writes.
// Reference: reference/Mercury_Dust_V30_Groove_CORRIGE_Reference.html.
// Not pixel-accurate V30! No hardware safety certification.
korg.app("Mercury V30", "TOOLS");

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

function clamp(a, lo, hi) {
  if (a < lo) return lo;
  if (a > hi) return hi;
  return a;
}
function wave(p) {
  // Triangle-sine approximation: signed, continuous, no floats or trig API.
  let q = p & 255;
  let r = q & 127;
  let u = r < 64 ? r : 128 - r;
  let shaped = (u * (128 - u)) / 32;
  return q < 128 ? shaped : -shaped;
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
function drawMatter() {
  if (!opened || menuOpen) return;
  korg.display.clear();
  let scene = v[0];
  let rx = (energy * v[3]) / 100;
  let width = 6 + v[1] / 35;
  let modulation = v[6] + v[7] / 3;
  let p = phase;
  if (v[5] < 20) p = (phase / 32) * 32;
  else if (v[5] < 50) p = (phase / 8) * 8;

  let x = 0;
  while (x < 128) {
    let s1 = wave(x * 3 + p + scene * 17);
    let s2 = wave(x * 7 - p / 2 + 39);
    let center = 23 + s1 * modulation / 1300 + s2 / 24;
    let thick = width + (wave(x * 4 + p * 2 + 64) + 128) / 36 + rx / 40;
    if (scene == 1 || scene == 5) thick -= 3;
    if (scene == 4 || scene == 7) thick += 3;
    thick = clamp(thick, 2, 19);

    let y = clamp(center - thick, 0, 63);
    let bottom = clamp(center + thick, y + 1, 64);
    if (v[8] > 20 && ((x + stepPos * 8) & 31) < v[8] / 6) {
      y = clamp(y + rx / 15, 0, 63);
      bottom = clamp(bottom + rx / 15, y + 1, 64);
    }
    korg.display.rect(x, y, 8, bottom - y);

    // Travelling black river and a moving metallic highlight.
    let slot = clamp(center + wave(x * 5 - p + 72) / 16, y, bottom - 1);
    let holeHeight = clamp(1 + v[9] / 35, 1, 4);
    korg.display.clearRect(x, slot, 8, clamp(holeHeight, 1, bottom - slot));
    if ((x & 31) == 0) {
      let rim = clamp(y + 1, y, bottom - 1);
      korg.display.clearRect(x, rim, 8, 1);
    }
    x += 8;
  }

  // Optional counter-moving ribbon. Higher cord counts are not ported yet.
  if (v[2] > 1) {
    x = 0;
    while (x < 128) {
      let a = wave(x * 4 - p + 120);
      let b = wave(x * 2 + p / 3 + 11);
      let center2 = 46 + a / 17 + b / 23;
      let width2 = 2 + (wave(x * 6 + p + scene * 29) + 128) / 44;
      if (scene == 3 || scene == 6) width2 += 2;
      width2 = clamp(width2, 1, 8);
      let y2 = clamp(center2 - width2, 0, 63);
      let end2 = clamp(center2 + width2, y2 + 1, 64);
      korg.display.rect(x, y2, 8, end2 - y2);
      if ((x & 31) == 0) {
        let slot2 = clamp(center2, y2, end2 - 1);
        korg.display.clearRect(x, slot2, 8, 1);
      }
      x += 8;
    }
  }
  if (v[10] > 50 && flash > 0) {
    let lineY = clamp((stepPos * 13 + phase / 7) & 63, 0, 63);
    korg.display.clearRect(0, lineY, 128, 1);
  }
  korg.display.number(scene + 1, 119, 55);
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
    else { storeAll(); drawMatter(); }
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
  if (index == 9) knobReact = clamp(value / 10, 0, 100);
});
korg.onEvent("frame", () => {
  if (!opened || menuOpen) return;
  frames += 1;
  if (energy > 0) energy = clamp(energy - 4, 0, 127);
  if (flash > 0) flash -= 1;
  if ((frames & 1) != 0) return;
  phase += (1 + v[4] * 2) + knobReact / 25;
  phase &= 2047;
  if (v[11] > 30 && ((frames + stepPos) % 18) < v[11] / 20) return;
  drawMatter();
});
