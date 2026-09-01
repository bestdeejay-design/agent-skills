import json
from datetime import datetime
from typing import List, Dict, Any
from ..agents.base import Issue


def generate_report(meta: Dict[str, Any], issues: List[Issue], output_format: str = "both") -> Dict[str, str]:
    reports = {}
    
    if output_format in ("json", "both"):
        reports["json"] = generate_json(meta, issues)
    
    if output_format in ("markdown", "both"):
        reports["markdown"] = generate_markdown(meta, issues)
    
    return reports


def generate_json(meta: Dict[str, Any], issues: List[Issue]) -> str:
    summary = {}
    for issue in issues:
        summary[issue.severity] = summary.get(issue.severity, 0) + 1
    
    report = {
        "meta": meta,
        "issues": [vars(issue) for issue in issues],
        "summary": summary
    }
    
    return json.dumps(report, indent=2, ensure_ascii=False)


def generate_markdown(meta: Dict[str, Any], issues: List[Issue]) -> str:
    lines = []
    lines.append("# Docs Audit Report\n")
    lines.append(f"**Project:** {meta.get('project_path', 'N/A')}")
    lines.append(f"**Level:** {meta.get('level', 'N/A')}")
    lines.append(f"**Date:** {datetime.now().isoformat()}")
    lines.append(f"**Total docs:** {meta.get('total_docs', 0)}")
    lines.append("")
    
    lines.append("## Summary\n")
    summary = {}
    for issue in issues:
        summary[issue.severity] = summary.get(issue.severity, 0) + 1
    
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for sev in ["critical", "warning", "nit"]:
        if sev in summary:
            lines.append(f"| {sev.capitalize()} | {summary[sev]} |")
    lines.append(f"| **Total** | **{len(issues)}** |")
    lines.append("")
    
    if issues:
        lines.append("## Issues\n")
        by_severity = {}
        for issue in issues:
            by_severity.setdefault(issue.severity, []).append(issue)
        
        for severity in ["critical", "warning", "nit"]:
            if severity in by_severity:
                lines.append(f"### {severity.upper()}\n")
                for issue in by_severity[severity]:
                    lines.append(f"**File:** {issue.file}")
                    if issue.line:
                        lines.append(f"**Line:** {issue.line}")
                    lines.append(f"\n{issue.description}\n")
                    if issue.fix:
                        lines.append(f"**Fix:** {issue.fix}\n")
    else:
        lines.append("## Issues\n")
        lines.append("✅ No issues found!\n")
    
    return "\n".join(lines)
