#!/usr/bin/env node
/**
 * Capture graham-bell screenshots: local FastAPI UI + static Vercel demo.
 * Usage (repo root, deps installed):
 *   node scripts/capture-demo-screenshots.mjs
 */
import { spawn } from "node:child_process";
import { mkdir, mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "docs", "demo");

async function waitFor(url, attempts = 40) {
  for (let i = 0; i < attempts; i++) {
    try {
      const res = await fetch(url);
      if (res.ok) return;
    } catch {
      /* retry */
    }
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error(`Server not ready: ${url}`);
}

async function main() {
  await mkdir(OUT, { recursive: true });

  const demoRoot = await mkdtemp(path.join(tmpdir(), "vx-shot-"));
  const dirs = ["source", "staging", "results", "retrieved"];
  for (const d of dirs) await mkdir(path.join(demoRoot, d), { recursive: true });
  await writeFile(path.join(demoRoot, "source", "payload.txt"), "sample payload\n");
  await writeFile(path.join(demoRoot, "source", "meta.txt"), "run: 42\n");
  const cfg = path.join(demoRoot, "config.yaml");
  await writeFile(
    cfg,
    [
      "backend: local",
      `source_dir: ${demoRoot}/source`,
      `staging_dir: ${demoRoot}/staging`,
      `results_dir: ${demoRoot}/results`,
      `retrieve_to: ${demoRoot}/retrieved`,
      "",
    ].join("\n"),
  );

  const py = path.join(ROOT, ".venv", "bin", "python");
  const server = spawn(
    py,
    ["-m", "uvicorn", "verified_xfer.web.app:app", "--host", "127.0.0.1", "--port", "8765"],
    { cwd: ROOT, stdio: ["ignore", "pipe", "pipe"], env: { ...process.env, PYTHONPATH: path.join(ROOT, "src") } },
  );
  server.stderr.on("data", () => {});

  const browser = await chromium.launch();
  try {
    await waitFor("http://127.0.0.1:8765/api/health");

    const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
    await page.goto("http://127.0.0.1:8765/", { waitUntil: "networkidle" });
    await page.check("#dry_run");
    await page.fill("#config_path", cfg);
    await page.click("#run-btn");
    await page.waitForFunction(
      () => document.getElementById("status-pill")?.textContent === "success",
      null,
      { timeout: 15000 },
    );
    await page.screenshot({
      path: path.join(OUT, "web-ui-stage.png"),
      fullPage: true,
    });
    console.log("wrote docs/demo/web-ui-stage.png");

    // Static demo (file://) — replay
    const demoPage = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const demoUrl = "file://" + path.join(ROOT, "demo", "index.html");
    await demoPage.goto(demoUrl, { waitUntil: "domcontentloaded" });
    await demoPage.selectOption("#command", "stage");
    await demoPage.click("#run-btn");
    await demoPage.waitForFunction(
      () => document.getElementById("status-pill")?.textContent === "success",
      null,
      { timeout: 15000 },
    );
    await demoPage.waitForTimeout(400);
    await demoPage.screenshot({
      path: path.join(OUT, "vercel-demo-replay.png"),
      fullPage: true,
    });
    console.log("wrote docs/demo/vercel-demo-replay.png");
  } finally {
    await browser.close();
    server.kill("SIGTERM");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
