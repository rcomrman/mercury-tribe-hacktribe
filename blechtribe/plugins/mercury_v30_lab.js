// Mercury Dust / BLECHTRIBE — V30-inspired LCD proof of concept
// Target: BLECHTRIBE plugin API (integer-only subset of JavaScript).
// LAB ONLY: not a pixel-accurate port of the archived V30 HTML.
// This app NEVER writes audio, part parameters, samples or patterns.
korg.app("Mercury V30", "TOOLS");

let opened = 0;
let phase = 0;
let frames = 0;
let stepPos = 0;
let energy = 0;
let mode = 0;
let knobReact = 40;

function triangle(value) {
  let p = value & 255;
  if (p < 128) return p - 64;
  return 192 - p;
}

function clamp(value, lo, hi) {
  if (value < lo) return lo;
  if (value > hi) return hi;
  return value;
}

function draw() {
  if (!opened) return;
  korg.display.clear();

  // Ribbon A: irregular chrome body, punched with moving black cavities.
  let x = 0;
  while (x < 128) {
    let s1 = triangle(x * 3 + phase + mode * 17);
    let s2 = triangle(x * 7 - phase / 2 + 39);
    let center = 23 + s1 / 9 + s2 / 16;
    let thick = 6 + (triangle(x * 4 + phase * 2 + 64) + 64) / 24;
    thick += energy / 40;
    if (mode == 1 || mode == 5) thick -= 2;
    if (mode == 4 || mode == 7) thick += 3;
    thick = clamp(thick, 2, 18);

    let y = clamp(center - thick, 0, 63);
    let bottom = clamp(center + thick, y + 1, 64);
    if (mode >= 4 && ((x + stepPos * 4) & 31) < 4) {
      y = clamp(y + energy / 16, 0, 63);
      bottom = clamp(bottom + energy / 16, y + 1, 64);
    }
    korg.display.rect(x, y, 4, bottom - y);

    let hollow = clamp(center + triangle(x * 5 - phase + 72) / 18, y, bottom - 1);
    korg.display.clearRect(x, hollow, 4, 1);
    if (x % 16 == 0) {
      let nick = clamp(y + 2, y, bottom - 1);
      korg.display.clearRect(x, nick, 4, 1);
    }
    x += 4;
  }

  // Ribbon B: a narrower, counter-moving metallic strand.
  x = 0;
  while (x < 128) {
    let a = triangle(x * 4 - phase + 120);
    let b = triangle(x * 2 + phase / 3 + 11);
    let center2 = 46 + a / 14 + b / 20;
    let width2 = 2 + (triangle(x * 6 + phase + mode * 29) + 64) / 35;
    if (mode == 3 || mode == 6) width2 += 2;
    width2 = clamp(width2, 1, 8);
    let y2 = clamp(center2 - width2, 0, 63);
    let end2 = clamp(center2 + width2, y2 + 1, 64);
    korg.display.rect(x, y2, 4, end2 - y2);
    if (x % 24 == 0) {
      let hole = clamp(center2, y2, end2 - 1);
      korg.display.clearRect(x, hole, 4, 1);
    }
    x += 4;
  }

  // Tiny preset number, not a permanent software menu.
  korg.display.number(mode + 1, 120, 55);
}

korg.onEvent("open", () => {
  opened = 1;
  phase = 0;
  frames = 0;
  draw();
});

korg.onEvent("close", () => {
  opened = 0;
});

korg.onEvent("buttonPress", (key) => {
  if (!opened) return;
  if (key == korg.key.PART_RIGHT) mode = (mode + 1) % 8;
  if (key == korg.key.PART_LEFT) mode = (mode + 7) % 8;
});

korg.onEvent("pad", (index, down, velocity) => {
  if (!opened || !down) return;
  energy = clamp(velocity, 20, 127);
});

korg.onEvent("step", (step) => {
  stepPos = step;
  if ((step & 3) == 0) energy = 96;
  else if (energy < 30) energy = 30;
});

korg.onEvent("knob", (index, value) => {
  if (!opened) return;
  if (index == 10) knobReact = clamp(value / 10, 0, 100);
});

korg.onEvent("frame", () => {
  if (!opened) return;
  frames += 1;
  if (energy > 0) energy = clamp(energy - 4, 0, 127);
  // 25 Hz input / 2 = 12.5 Hz visual preview.
  if ((frames & 1) != 0) return;
  phase += 2 + mode + knobReact / 25;
  phase &= 2047;
  draw();
});
