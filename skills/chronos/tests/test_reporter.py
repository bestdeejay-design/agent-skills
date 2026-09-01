import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chronos.core.reporter import generate_report, generate_json, generate_markdown
from chronos.agents.base import Issue


class TestReporter:
    def setup_method(self):
        self.meta = {
            "project_path": "/test/project",
            "preset": "full",
            "total_docs": 5
        }
        self.issues = [
            Issue(
                severity="critical",
                category="contradiction",
                file="docs/API.md",
                description="Deprecated endpoint",
                line=42
            ),
            Issue(
                severity="warning",
                category="duplicate",
                file="docs/VISION.md",
                description="High similarity with docs/ROADMAP.md",
                related_file="docs/ROADMAP.md",
                fix="Merge documents"
            ),
            Issue(
                severity="nit",
                category="orphan",
                file="docs/OLD.md",
                description="Document without links"
            ),
        ]
    
    def test_generate_json(self):
        result = generate_json(self.meta, self.issues)
        data = json.loads(result)
        assert "meta" in data
        assert "issues" in data
        assert "summary" in data
        assert data["meta"]["total_docs"] == 5
        assert len(data["issues"]) == 3
        assert data["summary"]["critical"] == 1
        assert data["summary"]["warning"] == 1
        assert data["summary"]["nit"] == 1
    
    def test_generate_markdown(self):
        result = generate_markdown(self.meta, self.issues)
        assert "# Docs Audit Report" in result
        assert "critical" in result.lower() or "CRITICAL" in result
        assert "warning" in result.lower() or "WARNING" in result
        assert "Deprecated endpoint" in result
    
    def test_generate_markdown_no_issues(self):
        result = generate_markdown(self.meta, [])
        assert "No issues found" in result
    
    def test_generate_report_both(self):
        reports = generate_report(self.meta, self.issues, "both")
        assert "json" in reports
        assert "markdown" in reports
    
    def test_generate_report_json_only(self):
        reports = generate_report(self.meta, self.issues, "json")
        assert "json" in reports
        assert "markdown" not in reports
    
    def test_generate_report_markdown_only(self):
        reports = generate_report(self.meta, self.issues, "markdown")
        assert "markdown" in reports
        assert "json" not in reports
