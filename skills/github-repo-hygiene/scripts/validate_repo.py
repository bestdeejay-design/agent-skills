#!/usr/bin/env python3
"""Run the skill's 16-point repo hygiene checklist (gh API + local files).

Covers references/community-checklist.md:
  A.1-A.6  files present/recognized (README, i18n sync, LICENSE spdx, CoC,
           CONTRIBUTING/SECURITY/SUPPORT, issue/PR templates)
  B.7-B.11 description, topics, homepage (Pages), social preview (warning),
           CI workflows (warning)
  C.12-C.13 community profile (health_percentage >= 100), discussions
  D.14-D.15 release exists, CHANGELOG updated
  E.16     git state clean, commits exist

Pure Python 3 stdlib. Requires `gh` CLI + auth for any API-backed check
(skipped otherwise with status="skipped"; use --local-only to skip them).

Usage:
    python3 validate_repo.py                 # repo auto-detected from git remote
    python3 validate_repo.py owner/repo
    python3 validate_repo.py --local-only    # filesystem checks only
    python3 validate_repo.py --json          # machine-readable report

Exit codes: 0 = no failed checks, 1 = failed checks, 2 = error.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd, timeout=30):
    """Run a command; returns (returncode, stdout)."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout.strip()
    except FileNotFoundError:
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, ""


def detect_repo() -> str:
    code, out = run(["git", "config", "--get", "remote.origin.url"])
    if code != 0 or not out:
        return ""
    url = out.strip()
    m = re.search(r"(?:github\.com[:/])([^/\s]+)/([^/\s]+?)(?:\.git)?$", url)
    if not m:
        return ""
    return f"{m.group(1)}/{m.group(2)}"


def gh_api(endpoint):
    code, out = run(["gh", "api", endpoint])
    if code != 0:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def gh_repo_view(repo, fields=None):
    cmd = ["gh", "repo", "view", repo, "--json", fields or "description,homepageUrl"]
    code, out = run(cmd)
    if code != 0:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def check(path: Path) -> bool:
    return path.exists() and path.is_file()


def headings(path: Path):
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    return re.findall(r"^(#{1,2})\s+(.+)$", text, re.MULTILINE)


def heading_levels(path: Path):
    """Just the level sequence (structure), not text — translations differ."""
    return [len(h) for h, _ in headings(path)]


class Checker:
    def __init__(self, repo: str, local_only: bool, local_ok: bool = False):
        self.repo = repo
        self.local_only = local_only
        self.local_ok = local_ok  # True when CWD is actually the repo (or a clone)
        self.passed = []
        self.failed = []
        self.warnings = []
        self.skipped = []

    def ok(self, item):
        self.passed.append(item)

    def fail(self, item, reason, fix_suggestion=""):
        self.failed.append({"item": item, "reason": reason, "fix_suggestion": fix_suggestion})

    def warn(self, item, reason, fix_suggestion=""):
        self.warnings.append({"item": item, "reason": reason, "fix_suggestion": fix_suggestion})

    def skip(self, item, reason):
        self.skipped.append({"item": item, "reason": reason})

    # ---- A. Files ----

    def check_a1_readme(self):
        if check(Path("README.md")):
            self.ok("A.1 README.md exists")
        else:
            self.fail("A.1 README.md", "README.md not found", "Create README.md (English, main page)")

    def check_a2_i18n_sync(self):
        lang_readmes = sorted(Path(".").glob("README.*.md"))
        if not lang_readmes:
            self.warn("A.2 README.<lang>.md", "no localized README found (ok if project is EN-only)")
            return
        en_levels = heading_levels(Path("README.md"))
        mismatched = []
        for lr in lang_readmes:
            if heading_levels(lr) != en_levels:
                mismatched.append(f"{lr.name}: heading structure differs (levels {heading_levels(lr)} vs {en_levels})")
        if mismatched:
            self.fail("A.2 i18n sync", "; ".join(mismatched),
                      "Mirror heading structure (level sequence) 1:1 between README.md and README.<lang>.md")
        else:
            self.ok("A.2 README.<lang>.md heading structure in sync")

    def check_a3_license(self):
        if check(Path("LICENSE")):
            self.ok("A.3 LICENSE present")
        else:
            self.fail("A.3 LICENSE", "LICENSE not found", "Add LICENSE (root; .github/ is NOT recognized)")

    def check_a3_license_spdx(self):
        if self.local_only:
            self.skip("A.3 LICENSE recognized", "requires gh (--local-only)")
            return
        data = gh_api(f"repos/{self.repo}/license")
        if data is None:
            self.warn("A.3 LICENSE recognized", "gh API call failed — cannot verify spdx_id")
        elif data.get("license") and data["license"].get("spdx_id"):
            self.ok(f"A.3 LICENSE recognized (spdx_id={data['license']['spdx_id']})")
        else:
            self.fail("A.3 LICENSE recognized", f"GitHub does not recognize license (got: {data.get('license')})",
                      "Use a canonical SPDX license text (e.g. MIT via github licenses API)")

    def check_a4_coc(self):
        path = Path("CODE_OF_CONDUCT.md")
        if not check(path):
            self.fail("A.4 CODE_OF_CONDUCT.md", "not found",
                      "Add full Contributor Covenant 2.1 text with contact email")
            return
        text = path.read_text(encoding="utf-8", errors="replace")
        if "Contributor Covenant" not in text and "contributor-covenant" not in text.lower():
            self.warn("A.4 CODE_OF_CONDUCT.md", "does not look like Contributor Covenant text",
                      "GitHub recognizes Covenant only (key: contributor_covenant)")
        else:
            self.ok("A.4 CODE_OF_CONDUCT.md present (Contributor Covenant)")

    def check_a5_community_files(self):
        missing = [f for f in ("CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md") if not check(Path(f))]
        if missing:
            self.fail("A.5 CONTRIBUTING/SECURITY/SUPPORT", f"missing: {', '.join(missing)}",
                      "Add these files (SUPPORT.md strictly uppercase name)")
        else:
            self.ok("A.5 CONTRIBUTING.md, SECURITY.md, SUPPORT.md present")

    def check_a6_templates(self):
        issues = []
        template_dir = Path(".github/ISSUE_TEMPLATE")
        if template_dir.is_dir():
            yml_forms = sorted(template_dir.glob("*.yml")) + sorted(template_dir.glob("*.yaml"))
            if not yml_forms:
                issues.append("no .yml issue forms in .github/ISSUE_TEMPLATE/")
        else:
            issues.append(".github/ISSUE_TEMPLATE/ missing")
        if not check(Path(".github/pull_request_template.md")):
            issues.append(".github/pull_request_template.md missing")
        if issues:
            self.fail("A.6 issue/PR templates", "; ".join(issues),
                      "Add yml issue forms (name+description frontmatter) and PR template (name+about)")
        else:
            self.ok("A.6 issue/PR templates present")

    # ---- B. Metadata ----

    def check_b7_description(self):
        if self.local_only:
            self.skip("B.7 description", "requires gh (--local-only)")
            return
        data = gh_repo_view(self.repo, "description")
        if data is None:
            self.skip("B.7 description", "gh repo view failed")
            return
        desc = data.get("description") or ""
        if not desc:
            self.fail("B.7 description", "repository description is empty",
                      "gh repo edit --description '<full description with keywords>'")
        elif len(desc) > 350:
            self.fail("B.7 description", f"description too long: {len(desc)} chars (UI limit 350)",
                      "Trim description to <= 350 chars")
        else:
            self.ok(f"B.7 description set ({len(desc)} chars)")

    def check_b8_topics(self):
        if self.local_only:
            self.skip("B.8 topics", "requires gh (--local-only)")
            return
        data = gh_api(f"repos/{self.repo}/topics")
        if data is None:
            self.skip("B.8 topics", "gh api topics failed")
            return
        topics = data.get("names", [])
        problems = []
        if not topics:
            problems.append("no topics")
        if len(topics) > 20:
            problems.append(f"{len(topics)} topics (limit 20)")
        for t in topics:
            if len(t) > 50:
                problems.append(f"topic {t!r} > 50 chars")
            if t != t.lower() or not re.fullmatch(r"[a-z0-9\-]+", t):
                problems.append(f"topic {t!r} not lowercase/alnum-hyphen")
        if problems:
            self.fail("B.8 topics", "; ".join(problems),
                      "gh api -X PUT repos/<owner>/<repo>/topics -f 'names[]=...' (full replace)")
        else:
            self.ok(f"B.8 topics ok ({', '.join(topics[:6])}{'...' if len(topics) > 6 else ''})")

    def check_b9_homepage(self):
        if self.local_only:
            self.skip("B.9 homepage", "requires gh (--local-only)")
            return
        pages = gh_api(f"repos/{self.repo}/pages")
        repo = gh_repo_view(self.repo, "homepageUrl")
        if pages is None:
            self.ok("B.9 homepage — Pages not enabled (no requirement)")
            return
        homepage = (repo or {}).get("homepageUrl") or ""
        if not homepage:
            self.fail("B.9 homepage (Pages)", "Pages enabled but homepage empty",
                      "gh repo edit --homepage https://<owner>.github.io/<repo>/")
        else:
            self.ok(f"B.9 homepage set: {homepage}")

    def check_b10_social_preview(self):
        candidates = []
        for pattern in ("og-image*", "social*", "preview*", "twitter-card*"):
            candidates.extend(sorted(Path(".").glob(pattern)))
            if Path("docs").is_dir():
                candidates.extend(sorted(Path("docs").glob(pattern)))
        if any(c.is_file() for c in candidates):
            self.ok("B.10 social preview image found (verify upload in Settings → Social preview)")
        else:
            self.warn("B.10 social preview", "no og-image/social image found in root/docs",
                      "Upload 1280x640 PNG/JPG (<1MB) via Settings → Social preview (UI only)")

    def check_b11_ci(self):
        if any(Path(".github/workflows").glob("*.yml")) or any(Path(".github/workflows").glob("*.yaml")):
            self.ok("B.11 CI workflow present (verify badge freshness manually)")
        else:
            self.warn("B.11 CI", "no .github/workflows/*.yml found",
                      "Add CI workflow; ensure badges in README reflect real status")

    # ---- C. Community health ----

    def check_c12_community_profile(self):
        if self.local_only:
            self.skip("C.12 community profile", "requires gh (--local-only)")
            return
        data = gh_api(f"repos/{self.repo}/community/profile")
        if data is None:
            self.skip("C.12 community profile", "gh api community/profile failed")
            return
        health = data.get("health_percentage", 0)
        files = data.get("files", {})
        issues = []
        if health < 100:
            issues.append(f"health_percentage={health} (< 100)")
        for key, label in (("issue_template", "issue_template"),
                           ("pull_request_template", "pull_request_template")):
            if not files.get(key):
                issues.append(f"{label} not counted by GitHub")
        if issues:
            self.fail("C.12 community profile", "; ".join(issues),
                      "Fix file frontmatter (name+about for .md, name+description for .yml)")
        else:
            self.ok(f"C.12 community profile health=100 (files counted)")

    def check_c13_discussions(self):
        if self.local_only:
            self.skip("C.13 discussions", "requires gh (--local-only)")
            return
        data = gh_repo_view(self.repo, "hasDiscussionsEnabled")
        if data is None:
            self.skip("C.13 discussions", "gh repo view failed")
            return
        if data.get("hasDiscussionsEnabled"):
            self.ok("C.13 Discussions enabled")
        else:
            self.warn("C.13 Discussions", "has_discussions=false (desired for Q&A)",
                      "gh repo edit --enable-discussions")

    # ---- D. Releases ----

    def check_d14_release(self):
        if self.local_only:
            self.skip("D.14 release", "requires gh (--local-only)")
            return
        code, out = run(["gh", "release", "list", "-R", self.repo, "--limit", "1"])
        if code != 0:
            self.skip("D.14 release", "gh release list failed")
            return
        if out:
            self.ok(f"D.14 latest release: {out.splitlines()[0][:60]}")
        else:
            self.fail("D.14 release", "no releases found",
                      "gh release create vX.Y.Z --generate-notes --target main")

    def check_d15_changelog(self):
        path = Path("CHANGELOG.md")
        if not check(path):
            self.warn("D.15 CHANGELOG.md", "not found (optional, but recommended)",
                      "Add CHANGELOG.md in Keep a Changelog format")
            return
        if re.search(r"^##\s+\[?\d+\.\d+\.\d+", path.read_text(encoding="utf-8", errors="replace"), re.MULTILINE):
            self.ok("D.15 CHANGELOG.md present with semver entries")
        else:
            self.warn("D.15 CHANGELOG.md", "no semver entries found",
                      "Use Keep a Changelog format: ## [1.2.3] - date")

    # ---- E. Final ----

    def check_e16_git_state(self):
        code, out = run(["git", "status", "--porcelain"])
        if code != 0:
            self.warn("E.16 git state", "not a git repo or git unavailable")
            return
        if out.strip():
            self.warn("E.16 git state", "working tree has uncommitted changes",
                      "Commit & push before declaring done")
        else:
            code2, _ = run(["git", "log", "--oneline", "-1"])
            if code2 == 0:
                self.ok("E.16 git tree clean, commits exist")
            else:
                self.warn("E.16 git state", "clean tree but no commits yet")

    def run_local_checks(self):
        if not self.local_ok:
            for item in ("A.1 README.md", "A.2 README.<lang>.md", "A.3 LICENSE",
                         "A.4 CODE_OF_CONDUCT.md", "A.5 CONTRIBUTING/SECURITY/SUPPORT",
                         "A.6 issue/PR templates", "B.10 social preview", "B.11 CI",
                         "D.15 CHANGELOG.md", "E.16 git state"):
                self.skip(item, "repo not checked out locally — run from repo root or use --clone")
            return
        self.check_a1_readme()
        self.check_a2_i18n_sync()
        self.check_a3_license()
        self.check_a4_coc()
        self.check_a5_community_files()
        self.check_a6_templates()
        self.check_b10_social_preview()
        self.check_b11_ci()
        self.check_d15_changelog()
        self.check_e16_git_state()

    def run_api_checks(self):
        if not self.local_only:
            self.check_a3_license_spdx()
            self.check_b7_description()
            self.check_b8_topics()
            self.check_b9_homepage()
            self.check_c12_community_profile()
            self.check_c13_discussions()
            self.check_d14_release()

    def run_all(self):
        self.run_local_checks()
        self.run_api_checks()

    def report(self):
        return {
            "repo": self.repo or "(unknown)",
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "skipped": self.skipped,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="16-point repo hygiene checklist (gh API + filesystem)")
    parser.add_argument("repo", nargs="?", default=None, help="owner/repo (default: from git remote)")
    parser.add_argument("--local-only", action="store_true", help="skip all gh API checks")
    parser.add_argument("--clone", action="store_true",
                        help="clone repo to a temp dir and audit local files there")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON report")
    args = parser.parse_args()

    repo = args.repo or detect_repo()
    if not repo:
        print("error: cannot determine repository; pass owner/repo or run inside a git clone",
              file=sys.stderr)
        return 2
    if args.clone and args.local_only:
        print("error: --clone and --local-only are mutually exclusive", file=sys.stderr)
        return 2

    cwd_before = os.getcwd()
    tmpdir = None
    if args.clone:
        tmpdir = tempfile.mkdtemp(prefix="hygiene-")
        code, out = run(["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", tmpdir])
        if code != 0:
            shutil.rmtree(tmpdir, ignore_errors=True)
            print(f"error: clone failed ({out[:200]})", file=sys.stderr)
            return 2
        os.chdir(tmpdir)

    try:
        local_ok = args.clone or (detect_repo() == repo)
        checker = Checker(repo, args.local_only, local_ok=local_ok)
        checker.run_all()
        report = checker.report()
    finally:
        if tmpdir:
            os.chdir(cwd_before)
            shutil.rmtree(tmpdir, ignore_errors=True)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"repo: {report['repo']}")
        for item in report["passed"]:
            print(f"  [PASS] {item}")
        for f in report["failed"]:
            print(f"  [FAIL] {f['item']}: {f['reason']}")
            if f["fix_suggestion"]:
                print(f"          fix: {f['fix_suggestion']}")
        for w in report["warnings"]:
            print(f"  [WARN] {w['item']}: {w['reason']}")
            if w.get("fix_suggestion"):
                print(f"          fix: {w['fix_suggestion']}")
        for s in report["skipped"]:
            print(f"  [SKIP] {s['item']}: {s['reason']}")

    sys.exit(1 if report["failed"] else 0)


if __name__ == "__main__":
    sys.exit(main())