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
  new URL("../plugins/mercury_v30_lab.js", import.meta.url), "utf8"
);
const result = compile(source, { name: "Mercury V30" });
assert.ok(result.ok, result.errors?.map(formatError).join("\n"));
assert.equal(result.info.app?.group, "TOOLS");
assert.ok(result.blob.length < BUDGET.scriptBytes);

const device = new SimDevice();
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
device.post("knob", 9, 800); // OSC EDIT is knob index 9, read-only.
assert.deepEqual(device.run(12), [], "No faults on performance events");
const setting = i => loaded.script.vars[result.info.symbols.v.slot + i];
assert.equal(setting(0), 1, "PART_RIGHT should select preset 2");

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

const status = device.status().scripts[0];
console.log("OK: compiled bytecode:", result.blob.length, "bytes");
console.log("OK: API version:", result.info.apiVersion);
console.log("OK: variables:", result.info.vars);
console.log("OK: peak cost units per handler:", status.maxCost);
console.log("NOTE: no hardware timing/flash/visual fidelity tested.");
device.closeApp();
assert.deepEqual(device.run(2), [], "No faults on EXIT/close");
