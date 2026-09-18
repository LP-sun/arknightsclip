import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { mkdir } from "node:fs/promises";
import { setTimeout as delay } from "node:timers/promises";
import path from "node:path";

const require = createRequire(import.meta.url);
const { chromium } = require("../renderers/rhine/node_modules/playwright");

const repo = path.resolve(import.meta.dirname, "..");
const appRoot = path.join(repo, "resources", "RhineLabUI");
const output = path.join(repo, "reports", "rhinelab_reference");
const port = Number(process.env.RHINE_REFERENCE_PORT ?? 5174);
const base = `http://127.0.0.1:${port}`;

await mkdir(output, { recursive: true });

const server = process.env.RHINE_REFERENCE_EXTERNAL ? null : spawn(
  process.platform === "win32" ? "npm.cmd" : "npm",
  ["run", "dev", "--", "--host", "127.0.0.1", "--port", String(port)],
  { cwd: appRoot, stdio: ["ignore", "pipe", "pipe"], shell: process.platform === "win32" },
);
const stop = () => server?.kill();
process.on("exit", stop);
process.on("SIGINT", () => { stop(); process.exit(130); });

async function waitForServer() {
  const deadline = Date.now() + 30_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(base);
      if (response.ok) return;
    } catch {}
    await delay(250);
  }
  throw new Error(`RhineLabUI server did not become ready at ${base}`);
}

if (!process.env.RHINE_REFERENCE_EXTERNAL) await waitForServer();
async function capture(name, query, settle = 2500) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on("console", (message) => {
    if (message.type() === "error") console.error(`[browser] ${message.text()}`);
  });
  page.on("pageerror", (error) => console.error(`[pageerror] ${error.message}`));
  try {
    await page.goto(`${base}/${query}`, { waitUntil: "commit", timeout: 8_000 });
  } catch (error) {
    console.warn(`navigation timeout for ${name}; capturing current page: ${error.message}`);
  }
  // The app creates its WebGL canvas only after its boot state machine. Give
  // the GLTF loader and composer a bounded settle window; some frozen review
  // URLs intentionally keep the canvas hidden until the next state tick.
  await page.waitForTimeout(settle);
  await page.screenshot({ path: path.join(output, `source_${name}.png`), fullPage: false });
  console.log(`captured source_${name}.png`);
}

try {
  const only = process.env.RHINE_ONLY;
  if (!only || only === "boot") await capture("boot", "?freeze=1&time=7.0", 1800);
  if (!only || only === "array") await capture("array", "?scene=archive&freeze=1&time=26.5", 3000);
  if (!only || only === "closeup") await capture("closeup", "?scene=detail&freeze=1&time=31.5", 3500);
} finally {
  stop();
}
