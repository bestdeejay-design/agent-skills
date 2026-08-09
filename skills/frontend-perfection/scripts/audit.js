#!/usr/bin/env node
/**
 * frontend-perfection — Lighthouse runner on a STABLE API.
 *
 * Runs a real Chrome (channel=chrome by default) via chrome-launcher and the
 * Lighthouse Node API. Explicitly designed around the failures of the legacy
 * script that relied on Playwright internals:
 *
 *   - NO private fields like browser._impl_obj._connection._transport._ws_url
 *     (they broke when the transport became PipeTransport). chrome-launcher
 *     gives us a stable CDP port from its own public output.
 *   - Supports Lighthouse >= 13 where require('lighthouse') is no longer the
 *     function itself — falls back to require('lighthouse').default.
 *   - Self-resolves dependencies: local node_modules -> NODE_PATH -> global
 *     npm root, so it never dies with "Cannot find module".
 *
 * Usage:
 *   node audit.js --url http://localhost:8000/ [options]
 *
 * Options:
 *   --url <url>            target URL (required)
 *   --mobile               run mobile emulation (default when not --desktop)
 *   --desktop              run desktop preset (default when not --mobile)
 *   --threshold <n>        minimum per-category score to exit 0 (default 100)
 *   --out <file.json>      write compact JSON report
 *   --no-headless          run with visible Chrome window
 *   --only <category>      run a single Lighthouse category (performance,
 *                          accessibility, best-practices, seo)
 *
 * Exit codes: 0 = all measured categories >= threshold; 1 = at least one
 * category below threshold; 2 = runner error (missing module, bad URL, crash).
 */
"use strict";

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

/* ------------------------------------------------------------------ *
 * Dependency resolution — stable, isolated, multi-location.          *
 * ------------------------------------------------------------------ */
function resolveModule(name) {
  // 1. Local node_modules next to this script (npm i lighthouse chrome-launcher)
  const scriptDir = __dirname;
  const local = path.join(scriptDir, "node_modules", name);
  if (fs.existsSync(local)) return local;

  // 2. NODE_PATH (package managers like pnpm/yarn, or explicit env)
  if (process.env.NODE_PATH) {
    const viaEnv = path.join(process.env.NODE_PATH, name);
    if (fs.existsSync(viaEnv)) return viaEnv;
  }

  // 3. Global npm prefix (npm root -g), works on Node 22 setups where
  //    require() does not resolve global modules on its own.
  try {
    const globalRoot = execFileSync("npm", ["root", "-g"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    const globalPath = path.join(globalRoot, name);
    if (globalPath && fs.existsSync(globalPath)) return globalPath;
  } catch (_) {
    /* npm not available — continue */
  }
  return null;
}

function requireOrResolve(name, fallbackExtractor) {
  try {
    return require(name);
  } catch (_) {
    const resolved = resolveModule(name);
    if (!resolved) return null;
    let mod = require(resolved);
    if (fallbackExtractor && typeof mod === "function" && mod.default) {
      mod = mod.default;
    }
    return mod;
  }
}

/* ------------------------------------------------------------------ *
 * CLI                                                                 *
 * ------------------------------------------------------------------ */
function parseArgs(argv) {
  const args = { url: null, mobile: false, desktop: false, threshold: 100, out: null, headless: true, only: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    switch (a) {
      case "--url": args.url = argv[++i]; break;
      case "--mobile": args.mobile = true; break;
      case "--desktop": args.desktop = true; break;
      case "--threshold": args.threshold = parseInt(argv[++i], 10); break;
      case "--out": args.out = argv[++i]; break;
      case "--no-headless": args.headless = false; break;
      case "--only": args.only = argv[++i]; break;
      default:
        if (a.startsWith("--")) {
          console.error(`[frontend-perfection] Unknown option: ${a}`);
          process.exit(2);
        }
    }
  }
  if (!args.url) {
    console.error("[frontend-perfection] --url is required");
    process.exit(2);
  }
  if (!args.mobile && !args.desktop) args.mobile = true; // default
  if (args.mobile && args.desktop) {
    console.error("[frontend-perfection] Choose either --mobile or --desktop, not both");
    process.exit(2);
  }
  return args;
}

/* ------------------------------------------------------------------ *
 * Compact report — audit ids, not raw Lighthouse payload.            *
 * ------------------------------------------------------------------ */
const CATEGORY_KEY = {
  performance: "performance",
  accessibility: "accessibility",
  "best-practices": "best-practices",
  seo: "seo",
};

function buildReport(lhr, opts) {
  const categories = lhr.categories || {};
  const report = {
    requestedUrl: lhr.requestedUrl || opts.url,
    finalUrl: lhr.finalUrl || "",
    fetchTime: lhr.fetchTime || "",
    mode: opts.mobile ? "mobile" : "desktop",
    categories: {},
    failedAudits: [],
  };

  const selected = opts.only ? [CATEGORY_KEY[opts.only]].filter(Boolean) : Object.values(CATEGORY_KEY);
  const audits = lhr.audits || {};

  for (const key of selected) {
    const cat = categories[key];
    if (!cat) continue;
    report.categories[key] = Math.round(cat.score * 100);
    for (const ref of cat.auditRefs || []) {
      const audit = audits[ref.id];
      if (!audit) continue;
      const score = audit.score;
      const isFailed = score !== null && score < 1 && ref.weight > 0;
      if (isFailed) {
        report.failedAudits.push({
          id: audit.id,
          title: audit.title,
          score: audit.score,
          displayValue: audit.displayValue || "",
          weight: ref.weight,
        });
      }
    }
  }

  return report;
}

function thresholdOk(report, threshold) {
  const scores = Object.values(report.categories);
  if (scores.length === 0) return true; // nothing measured
  return scores.every((s) => s >= threshold);
}

/* ------------------------------------------------------------------ *
 * Main                                                                 *
 * ------------------------------------------------------------------ */
async function main() {
  const opts = parseArgs(process.argv.slice(2));

  const lighthouse = requireOrResolve("lighthouse", true);
  const chromeLauncher = requireOrResolve("chrome-launcher");

  if (!lighthouse) {
    console.error(
      "[frontend-perfection] lighthouse module not found.\n" +
        "  Install it: npm i lighthouse chrome-launcher  (in this script's dir)\n" +
        "  or globally: npm i -g lighthouse chrome-launcher, then export NODE_PATH=$(npm root -g)"
    );
    process.exit(2);
  }
  if (!chromeLauncher) {
    console.error(
      "[frontend-perfection] chrome-launcher module not found.\n" +
        "  Install it: npm i chrome-launcher"
    );
    process.exit(2);
  }

  // Lighthouse API: >= 13 exports a namespace with .default; older exports fn.
  const lighthouseFn = typeof lighthouse === "function" ? lighthouse : lighthouse.default;
  if (typeof lighthouseFn !== "function") {
    console.error("[frontend-perfection] Unexpected lighthouse export shape:", typeof lighthouse);
    process.exit(2);
  }

  const chromeOpts = {
    chromeFlags: opts.headless ? ["--headless=new", "--no-sandbox", "--disable-gpu"] : [],
    logLevel: "error",
  };
  if (typeof chromeLauncher.launch === "function") {
    // chrome-launcher v1.x — launch() is a static method. We pass channel via
    // port 0; the default channel already prefers the real installed Chrome.
    chromeOpts.chromePath = undefined;
  }

  let chrome;
  let result;
  try {
    chrome = await chromeLauncher.launch(chromeOpts);
    const runOpts = {
      port: chrome.port,
      output: "json",
      logLevel: "error",
      onlyCategories: opts.only ? [CATEGORY_KEY[opts.only]].filter(Boolean) : Object.values(CATEGORY_KEY),
    };
    if (opts.desktop) {
      runOpts.formFactor = "desktop";
      runOpts.screenEmulation = { mobile: false, width: 1350, height: 940, deviceScaleFactor: 1, disabled: false };
    } else {
      runOpts.formFactor = "mobile";
      runOpts.screenEmulation = { mobile: true, width: 412, height: 915, deviceScaleFactor: 2.625, disabled: false };
    }

    const runnerResult = await lighthouseFn(opts.url, runOpts, null);
    if (!runnerResult || !runnerResult.lhr) {
      console.error("[frontend-perfection] Lighthouse produced no report (is the URL reachable?)");
      process.exit(2);
    }
    result = buildReport(runnerResult.lhr, opts);
  } catch (err) {
    console.error("[frontend-perfection] Runner error:", err && err.stack ? err.stack : err);
    process.exit(2);
  } finally {
    if (chrome) {
      try {
        await chrome.kill();
      } catch (_) {
        /* already dead */
      }
    }
  }

  if (opts.out) {
    fs.writeFileSync(opts.out, JSON.stringify(result, null, 2), "utf8");
    console.log(`[frontend-perfection] Report written to ${opts.out}`);
  }

  console.log(`\n[frontend-perfection] ${result.mode} audit of ${result.finalUrl || result.requestedUrl}`);
  console.log(`  fetched: ${result.fetchTime}`);
  for (const [key, score] of Object.entries(result.categories)) {
    console.log(`  ${key.padEnd(16)} ${score}/100`);
  }
  if (result.failedAudits.length) {
    console.log(`\n  Failed audits (${result.failedAudits.length}):`);
    for (const a of result.failedAudits) {
      console.log(`    - ${a.id}  (score ${Math.round(a.score * 100)}, weight ${a.weight})  ${a.title}${a.displayValue ? " — " + a.displayValue : ""}`);
    }
  } else {
    console.log("\n  No failed weighted audits.");
  }

  process.exit(thresholdOk(result, opts.threshold) ? 0 : 1);
}

main().catch((err) => {
  console.error("[frontend-perfection] Fatal:", err);
  process.exit(2);
});