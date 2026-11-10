// Capture a short actual animation from the official GELUMPE reference VM.
// PGM images preserve the genuine 128x64 monochrome LCD pixels exactly.
import assert from "node:assert/strict";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";

const gelumpe = resolve(process.argv[2] ?? "../kuhlers-gelumpe");
const load = path => import(pathToFileURL(join(gelumpe, path)).href);
const [{ compile, formatError }, { SimDevice }] = await Promise.all([
  load("src/script/compiler.mjs"), load("src/script/sim.mjs")
]);
const src = await readFile(new URL("../plugins/mercury_r6_glitch_lab.js", import.meta.url), "utf8");
const output = compile(src, { name: "Mercury_R6" });
assert.ok(output.ok, output.errors?.map(formatError).join("\n"));
const device = new SimDevice();
const loaded = device.load(output.blob);
assert.ok(loaded.ok, loaded.error?.message);
assert.ok(device.openApp(0));
assert.deepEqual(device.run(4), []);

const dir = resolve("blechtribe/out/r6-motion");
await mkdir(dir, { recursive: true });
const hashes = new Set();
for (let frame = 0; frame < 48; frame++) {
  // One capture every completed 4-tile sweep (160ms); deliberately vary dynamics.
  if (frame % 2 === 0) device.post("step", frame % 16);
  if (frame % 8 === 0) device.post("pad", 0, 1, 80 + frame % 40);
  assert.deepEqual(device.run(4), [], "R6 runtime fault during motion at frame " + frame);
  const screen = device.display.bytes;
  const pixels = Buffer.alloc(128 * 64);
  for (let y = 0; y < 64; y++) for (let x = 0; x < 128; x++) {
    pixels[y * 128 + x] = (screen[(y >> 3) * 128 + x] >> (y & 7)) & 1 ? 255 : 0;
  }
  hashes.add(createHash("sha256").update(pixels).digest("hex"));
  const title = "f" + String(frame).padStart(3, "0") + ".pgm";
  await writeFile(join(dir, title), Buffer.concat([Buffer.from("P5\n128 64\n255\n"), pixels]));
}
assert.ok(hashes.size >= 30, "Not enough distinct frames for an evolving animation");
console.log("OK: 48 procedural monochrome frames captured, unique:", hashes.size);
console.log("NOTE: 6.25 full sweeps per second in the reference simulation, not verified on hardware.");
