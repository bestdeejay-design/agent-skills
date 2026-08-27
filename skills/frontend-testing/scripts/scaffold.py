#!/usr/bin/env python3
"""Scaffold frontend-testing configs into a target project.

Copies the reference configs from this skill's ``references/`` into a target
project directory, deterministically and inspectably. One command, one job:
emit the files the user needs to wire into CI, and print exactly what it did so
the run is *evidence* (a config that has never been placed is a draft, not a
scaffold).

Pure Python 3 standard library only. Deterministic: same inputs -> same outputs,
no network, no timestamps, no randomness. Safe to re-run (overwrites, never
deletes user files outside the mapped destinations).
"""

import argparse
import os
import shutil
import sys

# Layer -> (source reference file, default destination relative to --target).
# The reference files are the source of truth; this map is the only place the
# script decides where each layer lands.
LAYERS = {
    "playwright": ("references/playwright.config.ts", "playwright.config.ts"),
    "e2e": ("references/e2e-smoke.spec.ts", "e2e/e2e-smoke.spec.ts"),
    "a11y": ("references/a11y-test.md", "e2e/a11y-test.md"),
    "visual": ("references/visual-regression.md", "e2e/visual-regression.md"),
    "ci": ("references/ci-perf-budget.yml", ".github/workflows/perf-budget.yml"),
    "contract": ("references/contract-test.md", "tests/contract/contract-test.md"),
}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Scaffold frontend-testing configs into a target project."
    )
    parser.add_argument(
        "--target", required=True,
        help="Target project directory to scaffold configs into.",
    )
    parser.add_argument(
        "--layers", default="playwright,e2e,a11y,ci",
        help="Comma-separated layers to copy (default: playwright,e2e,a11y,ci). "
             "Valid: " + ", ".join(sorted(LAYERS)) + ".",
    )
    parser.add_argument(
        "--skill-dir",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="Path to this skill folder (auto-detected; override for testing).",
    )
    args = parser.parse_args(argv)

    target = os.path.abspath(args.target)
    if not os.path.isdir(target):
        print("ERROR: target directory does not exist: {}".format(target),
              file=sys.stderr)
        return 2

    layers = [l.strip() for l in args.layers.split(",") if l.strip()]
    unknown = [l for l in layers if l not in LAYERS]
    if unknown:
        print("ERROR: unknown layer(s): {}. Valid: {}".format(
            ", ".join(unknown), ", ".join(sorted(LAYERS))), file=sys.stderr)
        return 2

    copied = 0
    for layer in layers:
        src_rel, dst_rel = LAYERS[layer]
        src = os.path.join(args.skill_dir, src_rel)
        dst = os.path.join(target, dst_rel)
        if not os.path.isfile(src):
            print("ERROR: source reference missing: {}".format(src), file=sys.stderr)
            return 1
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        print("copied  {}  ->  {}".format(src_rel, dst_rel))
        copied += 1

    print("")
    print("Scaffolded {} file(s) into {}".format(copied, target))
    print("Next: wire CI (see references/ci-perf-budget.yml) and run the "
          "evidence gates in SKILL.md to prove the suite is green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
