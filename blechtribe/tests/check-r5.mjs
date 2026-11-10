// Run from the Mercury repo root:
//   node blechtribe/tests/check-mercury.mjs ../kuhlers-gelumpe
// Uses the OFFICIAL GELUMPE compiler and reference SimDevice, not a mock compiler.
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";

const gelumpe = resolve(process.argv[2] ?? "../kuhlers-gelumpe");
const importGelumpe = path => import(pathToFileURL(join(gelumpe, path)).href);

const [{ compile, formatError }, { SimDevice }, { KEY_NAMES }, { BUDGET }] =
  await Promise.all([
    importGelumpe("src/script/compiler.mjs"),
    importGelumpe("src/script/sim.mjs"),
    importGelumpe("data/script/names.mjs"),
    importGelumpe("data/script/contract.mjs"),
  ]);

const source = await readFile(
  new URL("../plugins/mercury_r5_coils_lab.js", import.meta.url), "utf8"
);
const result = compile(source, { name: "Mercury_R5" });
assert.ok(result.ok, result.errors?.map(formatError).join("\n"));
assert.equal(result.info.app?.group, "TOOLS");
assert.ok(result.info.symbols.FB.length === 256, "R5 uses packed 32x64 tiled render buffer");
assert.ok(result.blob.length < BUDGET.scriptBytes);

const cardStore = new Map();
const storage = {
  load: name => cardStore.get(name) ?? null,
  save: records => {
    for (const r of records) {
      assert.match(r.name, /^[A-Za-z][A-Za-z0-9_]{0,14}$/,
        "Stored plugin name must match the official SD format");
      cardStore.set(r.name, { mask: r.mask, values: Int32Array.from(r.values) });
    }
  },
};
const device = new SimDevice({ storage });
const loaded = device.load(result.blob);
assert.ok(loaded.ok, loaded.error?.message);
assert.ok(device.openApp(0), "App should open through BLECH TOOLS");
assert.deepEqual(device.run(12), [], "No faults on open or idle frames");
assert.ok(device.display.bytes.some(value => value !== 0),
  "Mercury should draw nonempty pixels");

const key = name => {
  const found = KEY_NAMES.find(entry => entry.name === name);
  assert.ok(found, "Missing key: " + name);
  return found.value;
};
// Preset can change in visual mode.
device.post("buttonPress", key("PART_RIGHT"));
device.post("step", 4);
device.post("pad", 0, 1, 100);
device.post("knob", 9, 255); // OSC EDIT (0..255) is knob index 9, read-only.
assert.deepEqual(device.run(12), [], "No faults on performance events");
const setting = i => loaded.script.vars[result.info.symbols.v.slot + i];
assert.equal(setting(0), 1, "PART_RIGHT should select preset 2");
assert.equal(loaded.script.vars[result.info.symbols.knobReact.slot], 100,
  "OSC EDIT maximum must scale to full visual range");

device.post("buttonPress", key("PART_LEFT"));
assert.deepEqual(device.run(4), [], "No faults on preset reversal");
assert.equal(setting(0), 0);

// Mercury pages are separate from Korg menu and preserve all 12 settings.
device.post("buttonPress", key("MENU"));
assert.deepEqual(device.run(2), [], "No faults opening Mercury settings");
assert.equal(loaded.script.vars[result.info.symbols.menuOpen.slot], 1);
device.post("buttonPress", key("BAR_4")); // preset +1
assert.deepEqual(device.run(2), [], "No faults editing preset");
assert.equal(setting(0), 1);
device.post("buttonPress", key("BAR_1")); // preset -1
assert.deepEqual(device.run(2), [], "No faults decrementing preset");
assert.equal(setting(0), 0);
device.post("buttonPress", key("EDIT_RIGHT"));
device.post("buttonPress", key("PART_RIGHT"));
device.post("buttonPress", key("BAR_3")); // smooth +10 (index 5)
assert.deepEqual(device.run(3), [], "No faults on second settings page");
assert.equal(setting(5), 84, "SMOOTH should be editable on movement page");
device.post("buttonPress", key("MENU"));
assert.deepEqual(device.run(4), [], "No faults exiting Mercury settings");
assert.equal(loaded.script.vars[result.info.symbols.menuOpen.slot], 0);

// Stress all eight visual scenes and validate no mode disables the VM.
const variables = loaded.script.vars;
for (let preset = 0; preset < 8; preset++) {
  variables[result.info.symbols.v.slot + 0] = preset;
  assert.deepEqual(device.run(6), [], "No faults in R5 preset " + preset);
  assert.ok(device.display.bytes.some(x => x), "Nonempty R5 scene " + preset);
  const earlyFrame = Uint8Array.from(device.display.bytes);
  assert.deepEqual(device.run(28), [], "No motion runtime faults in scene " + preset);
  assert.ok(earlyFrame.some((value, i) => value !== device.display.bytes[i]),
    "Scene " + preset + " must visibly evolve over time");
}
// Stress high-energy and extreme parameter combinations before publishing R5.
const profiles = [
  [7,100,8,100,5,100,100,100,100,100,100,0],
  [0,100,8,100,5,100,100,100,0,100,0,0],
  [4,100,2,100,5,75,100,85,100,85,100,0],
  [1,0,1,0,0,0,0,0,0,0,0,0],
];
for (let profile = 0; profile < profiles.length; profile++) {
  for (let index = 0; index < 12; index++)
    variables[result.info.symbols.v.slot + index] = profiles[profile][index];
  device.post("pad", 0, 1, 127);
  device.post("step", 0);
  assert.deepEqual(device.run(32), [], "No R5 faults under stress profile " + profile);
}

// Return to the first preset and ensure each global setting is in range.
variables[result.info.symbols.v.slot] = 0;
for (let i = 0; i < 12; i++) {
  const value = setting(i);
  const lo = i == 2 ? 1 : 0;
  const hi = i == 0 ? 7 : i == 2 ? 8 : i == 4 ? 5 : 100;
  assert.ok(value >= lo && value <= hi, "Setting " + i + " outside range");
}
device.post("buttonPress", key("MENU"));
assert.deepEqual(device.run(2), [], "Open menu before persistence test");
device.post("buttonPress", key("MENU"));
assert.deepEqual(device.run(3), [], "Close menu and request save");
assert.ok(cardStore.has("Mercury_R5"), "Store should save all settings");
const storedValue = setting(5);
const reboot = new SimDevice({ storage });
const rebootLoad = reboot.load(result.blob);
assert.ok(rebootLoad.ok, rebootLoad.error?.message);
assert.deepEqual(reboot.run(2), [], "No faults restoring from persistent storage");
assert.equal(rebootLoad.script.vars[result.info.symbols.v.slot + 5],
  storedValue, "SMOOTH setting survives simulated power cycle");

const status = device.status().scripts[0];
const maxCost = Math.max(...Object.values(status.maxCost));
assert.ok(maxCost <= 19500, "Guardrail: instruction cost too close to the 20000-unit VM ceiling: " + maxCost);
console.log("OK: compiled bytecode:", result.blob.length, "bytes");
console.log("OK: API version:", result.info.apiVersion);
console.log("OK: variables:", result.info.vars);
console.log("OK: peak cost units per handler:", status.maxCost);
console.log("NOTE: no hardware timing/flash/visual fidelity tested.");
device.closeApp();
assert.deepEqual(device.run(2), [], "No faults on EXIT/close");
