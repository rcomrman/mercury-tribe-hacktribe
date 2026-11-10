// Render a visual contact sheet from GELUMPE's OFFICIAL simulated LCD.
// This is an emulator snapshot, NOT a photograph of the Electribe's display.
import assert from "node:assert/strict";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { resolve, join } from "node:path";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";

const root = resolve(process.argv[2] ?? "../kuhlers-gelumpe");
const load = path => import(pathToFileURL(join(root, path)).href);
const [{ compile, formatError }, { SimDevice }] = await Promise.all([
  load("src/script/compiler.mjs"),
  load("src/script/sim.mjs"),
]);
const source = await readFile(new URL("../plugins/mercury_r4_braid_lab.js", import.meta.url), "utf8");
const result = compile(source, { name: "Mercury_R4" });
assert.ok(result.ok, result.errors?.map(formatError).join("\n"));
const d = new SimDevice();
const r = d.load(result.blob);
assert.ok(r.ok, r.error?.message);
assert.ok(d.openApp(0));
assert.deepEqual(d.run(2), []);
const vars = r.script.vars;
const modeSlot = result.info.symbols.v.slot;
const sceneNames = ["FLOW", "SILK", "HYPNOSE", "ACID", "HARD TEK", "LOFI", "JUNGLE", "COLLAPSE"];
let svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="1280" viewBox="0 0 1120 1280">';
svg += '<rect width="1120" height="1280" fill="#16191e"/>';
svg += '<text x="28" y="31" font-family="monospace" font-size="21" fill="#fafafa">MERCURY DUST / BLECHTRIBE — R4 BITMAP PREVIEW</text>';
svg += '<text x="28" y="54" font-family="monospace" font-size="12" fill="#9fa8b3">Simulated 128x64 LCD · 8 experimental modes · NOT the V30 reference</text>';
const hashes = new Set();
for (let i = 0; i < 8; i++) {
  vars[modeSlot] = i;
  assert.deepEqual(d.run(4), [], "No faults drawing mode " + i);
  const b = Uint8Array.from(d.display.bytes);
  hashes.add(createHash("sha256").update(b).digest("hex"));
  const baseX = 28 + (i % 2) * 548;
  const baseY = 78 + Math.floor(i / 2) * 293;
  svg += '<text x="' + baseX + '" y="' + baseY + '" font-family="monospace" font-size="16" fill="#f2f2f2">' + (i + 1) + ' — ' + sceneNames[i] + '</text>';
  svg += '<g transform="translate(' + baseX + ' ' + (baseY + 12) + ') scale(4)">';
  svg += '<rect width="128" height="64" fill="#000"/>';
  for (let y = 0; y < 64; y++) {
    let x = 0;
    while (x < 128) {
      if (((b[(y >> 3) * 128 + x] >> (y & 7)) & 1) == 0) { x += 1; continue; }
      const begin = x;
      while (x < 128 && ((b[(y >> 3) * 128 + x] >> (y & 7)) & 1) == 1) x += 1;
      svg += '<rect x="' + begin + '" y="' + y + '" width="' + (x - begin) + '" height="1" fill="#fff"/>';
    }
  }
  svg += '</g>';
}
assert.ok(hashes.size >= 4, "Fewer than four distinguishable scenes");
svg += '<text x="28" y="1264" font-family="monospace" font-size="13" fill="#b5bcc4">Non-final procedural prototype. No audio / DSP processing.</text>';
svg += '</svg>';
const out = resolve("blechtribe/out");
await mkdir(out, { recursive: true });
await writeFile(join(out, "mercury-r4-scenes.svg"), svg);
console.log("OK: wrote visual preview; unique snapshots:", hashes.size);
