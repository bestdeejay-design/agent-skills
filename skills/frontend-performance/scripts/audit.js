#!/usr/bin/env node
/**
 * frontend-performance — Lighthouse runner on a STABLE API.
 *
 * Ported shape from frontend-perfection/audit.js: real Chrome via
 * chrome-launcher, Lighthouse >= 13 support with .default fallback,
 * self-resolving dependencies (local node_modules -> NODE_PATH -> global
 * npm root), compact failed-audit JSON. This skill OWNS performance depth
 * (Core Web Vitals + the 43 Performance rules), so the default category is
 * `performance` and the report surfaces the CWV audits explicitly.
 *
 * Usage:
 *   node audit.js --url http://localhost:8000/ [options]
 *
 * Options:
 *   --url <url>            target URL (required)
 *   --mobile               run mobile emulation (default when not --desktop)
 *   --desktop              run desktop preset
 *   --threshold <n>        minimum performance score to exit 0 (default 90)
 *   --out <file.json>      write compact JSON report
 *   --no-headless          run with visible Chrome window
 *   --only <category>      run a single Lighthouse category (default: performance)
 *
 * Exit codes: 0 = performance >= threshold; 1 = below threshold; 2 = runner error.
 */
"use strict";

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

/* ------------------------------------------------------------------ *
 * Dependency resolution — stable, isolated, multi-location.          *
 * ------------------------------------------------------------------ */
function resolveModule(name) {
  const scriptDir = __dirname;
  const local = path.join(scriptDir, "node_modules", name);
  if (fs.existsSync(local)) return local;

  if (process.env.NODE_PATH) {
    const viaEnv = path.join(process.env.NODE_PATH, name);
    if (fs.existsSync(viaEnv)) return viaEnv;
  }

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
  const args = { url: null, mobile: false, desktop: false, threshold: 90, out: null, headless: true, only: null };
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
          console.error(`[frontend-performance] Unknown option: ${a}`);
          process.exit(2);
        }
    }
  }
  if (!args.url) {
    console.error("[frontend-performance] --url is required");
    process.exit(2);
  }
  if (!args.mobile && !args.desktop) args.mobile = true;
  if (args.mobile && args.desktop) {
    console.error("[frontend-performance] Choose either --mobile or --desktop, not both");
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

// Core Web Vitals + key perf audits we always surface by id.
const CWV_AUDITS = [
  "largest-contentfulpaint", "first-contentful-paint",
  "interactive", "cumulative-layout-shift", "total-blocking-time",
  "speed-index", "server-response-time", "mainthread-work-breakdown",
  "render-blocking-resources", "uses-text-compression",
  "uses-http2", "uses-rel-preconnect", "uses-rel-preload",
  "efficient-animated-content", "dom-size", "bootup-time",
  "network-requests", "total-byte-weight", "uses-long-cache-ttl",
  "offscreen-images", "unminified-javascript", "unused-javascript",
  "legacy-javascript", "redirects",
];

function buildReport(lhr, opts) {
  const categories = lhr.categories || {};
  const report = {
    requestedUrl: lhr.requestedUrl || opts.url,
    finalUrl: lhr.finalUrl || "",
    fetchTime: lhr.fetchTime || "",
    mode: opts.mobile ? "mobile" : "desktop",
    categories: {},
    cwv: {},
    failedAudits: [],
  };

  const selected = opts.only ? [CATEGORY_KEY[opts.only]].filter(Boolean) : ["performance"];
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

  // Surface CWV numeric values regardless of pass/fail.
  for (const id of CWV_AUDITS) {
    const a = audits[id];
    if (a) {
      report.cwv[id] = {
        score: a.score,
        displayValue: a.displayValue || "",
        numericValue: typeof a.numericValue === "number" ? a.numericValue : null,
      };
    }
  }

  return report;
}

function thresholdOk(report, threshold) {
  const scores = Object.values(report.categories);
  if (scores.length === 0) return true;
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
      "[frontend-performance] lighthouse module not found.\n" +
        "  Install it: npm i lighthouse chrome-launcher  (in this script's dir)\n" +
        "  or globally: npm i -g lighthouse chrome-launcher, then export NODE_PATH=$(npm root -g)"
    );
    process.exit(2);
  }
  if (!chromeLauncher) {
    console.error(
      "[frontend-performance] chrome-launcher module not found.\n" +
        "  Install it: npm i chrome-launcher"
    );
    process.exit(2);
  }

  const lighthouseFn = typeof lighthouse === "function" ? lighthouse : lighthouse.default;
  if (typeof lighthouseFn !== "function") {
    console.error("[frontend-performance] Unexpected lighthouse export shape:", typeof lighthouse);
    process.exit(2);
  }

  const chromeOpts = {
    chromeFlags: opts.headless ? ["--headless=new", "--no-sandbox", "--disable-gpu"] : [],
    logLevel: "error",
  };

  let chrome;
  let result;
  try {
    chrome = await chromeLauncher.launch(chromeOpts);
    const runOpts = {
      port: chrome.port,
      output: "json",
      logLevel: "error",
      onlyCategories: opts.only ? [CATEGORY_KEY[opts.only]].filter(Boolean) : ["performance"],
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
      console.error("[frontend-performance] Lighthouse produced no report (is the URL reachable?)");
      process.exit(2);
    }
    result = buildReport(runnerResult.lhr, opts);
  } catch (err) {
    console.error("[frontend-performance] Runner error:", err && err.stack ? err.stack : err);
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
    console.log(`[frontend-performance] Report written to ${opts.out}`);
  }

  console.log(`\n[frontend-performance] ${result.mode} audit of ${result.finalUrl || result.requestedUrl}`);
  console.log(`  fetched: ${result.fetchTime}`);
  for (const [key, score] of Object.entries(result.categories)) {
    console.log(`  ${key.padEnd(16)} ${score}/100`);
  }
  if (Object.keys(result.cwv).length) {
    console.log(`\n  Core Web Vitals / key metrics:`);
    for (const [id, v] of Object.entries(result.cwv)) {
      console.log(`    - ${id.padEnd(28)} ${v.displayValue || (v.score == null ? "" : "score " + Math.round(v.score * 100))}`);
    }
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
  console.error("[frontend-performance] Fatal:", err);
  process.exit(2);
});
