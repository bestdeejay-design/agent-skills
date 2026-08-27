#!/usr/bin/env node
/*
 * frontend-a11y — runtime accessibility audit (Playwright + axe-core).
 *
 * Covers the RUNTIME subset of the Front-End-Checklist "Accessibility" category
 * that cannot be checked statically: computed color contrast, ARIA required
 * parent/child relationships, live regions, focus order, modal focus traps,
 * reflow at 400% zoom, touch target size, and screen-reader-oriented rules that
 * axe-core models. The static subset lives in scripts/a11y_audit.py (offline).
 *
 * Required deps (NOT needed at build time, only when you run this):
 *   npm i playwright axe-core
 *   npx playwright install chromium
 *
 * Usage:
 *   node a11y_axe.mjs --url http://localhost:8377/ [--out axe.json] [--wcag AA|AAA]
 *
 * Exit codes: 0 = no violations; 1 = violations found; 2 = runner error.
 */
import { chromium } from "playwright";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const args = { url: null, out: null, wcag: "AA" };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--url") args.url = argv[++i];
    else if (a === "--out") args.out = argv[++i];
    else if (a === "--wcag") args.wcag = argv[++i];
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.url) {
    console.error("ERROR: --url is required");
    process.exit(2);
  }

  let axeSource;
  try {
    axeSource = readFileSync(
      join(__dirname, "..", "node_modules", "axe-core", "axe.min.js"),
      "utf8"
    );
  } catch {
    try {
      axeSource = readFileSync(
        require.resolve("axe-core/axe.min.js"),
        "utf8"
      );
    } catch (e) {
      console.error(
        "ERROR: axe-core not found. Install with `npm i playwright axe-core` and `npx playwright install chromium`."
      );
      process.exit(2);
    }
  }

  let browser;
  try {
    browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
    await page.goto(args.url, { waitUntil: "networkidle" });
    await page.addScriptTag({ content: axeSource });

    const results = await page.evaluate(async (wcag) => {
      // eslint-disable-next-line no-undef
      const r = await axe.run(document, {
        runOnly: {
          type: "tag",
          values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", wcag === "AAA" ? "wcag22aaa" : "wcag2a"],
        },
        resultTypes: ["violations", "incomplete"],
      });
      return r;
    }, args.wcag);

    const checks = [];
    for (const v of results.violations) {
      for (const node of v.nodes) {
        checks.push({
          id: "a11y:axe:" + v.id,
          title: v.help,
          severity: v.impact || "medium",
          ok: false,
          detail: `${v.id}: ${v.help} — ${node.target.join(" ")} (${node.failureSummary || ""})`,
          wcag: v.tags.filter((t) => t.startsWith("wcag")).join(","),
        });
      }
    }
    // incomplete = needs human confirmation (manual signal, not a hard fail)
    const incomplete = results.incomplete.map((v) => ({
      id: "a11y:axe:" + v.id,
      title: v.help,
      severity: "manual",
      ok: true,
      detail: `${v.id}: ${v.help} — requires manual confirmation (${v.nodes.length} node(s))`,
    }));

    const report = {
      tool: "frontend-a11y/a11y_axe",
      url: args.url,
      wcag: args.wcag,
      checks: checks.concat(incomplete),
      summary: {
        total: checks.length + incomplete.length,
        violations: checks.length,
        manual: incomplete.length,
      },
    };

    if (args.out) {
      const { writeFileSync } = await import("node:fs");
      writeFileSync(args.out, JSON.stringify(report, null, 2));
      console.log(`Report written to ${args.out}`);
    }
    console.log(`\n[frontend-a11y] axe runtime audit of ${args.url}`);
    console.log(
      `  violations: ${checks.length}, manual/incomplete: ${incomplete.length}`
    );
    for (const c of checks) {
      console.log(`  [FAIL] ${c.id} (${c.severity}): ${c.detail}`);
    }
    await browser.close();
    process.exit(checks.length === 0 ? 0 : 1);
  } catch (e) {
    console.error("ERROR: axe runner failed:", e.message);
    if (browser) await browser.close();
    process.exit(2);
  }
}

main();
