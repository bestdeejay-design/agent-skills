import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chronos.agents.base import Issue, Document, BaseAgent


class TestIssue:
    def test_create_basic(self):
        issue = Issue(
            severity="warning",
            category="duplicate",
            file="docs/test.md",
            description="Test issue"
        )
        assert issue.severity == "warning"
        assert issue.category == "duplicate"
        assert issue.file == "docs/test.md"
        assert issue.line is None
        assert issue.related_file is None
        assert issue.fix == ""
    
    def test_create_with_all_fields(self):
        issue = Issue(
            severity="critical",
            category="broken_link",
            file="docs/API.md",
            description="Broken link",
            line=42,
            related_file="docs/other.md",
            fix="Update link"
        )
        assert issue.line == 42
        assert issue.related_file == "docs/other.md"


class TestDocument:
    def test_create(self):
        doc = Document(
            path="/test/docs/file.md",
            content="# Hello",
            mtime=1000.0,
            size=100
        )
        assert doc.path == "/test/docs/file.md"
        assert doc.content == "# Hello"
        assert doc.mtime == 1000.0
        assert doc.size == 100


class TestBaseAgent:
    def test_abstract(self):
        try:
            BaseAgent("test")
            assert False, "Should raise TypeError"
        except TypeError:
            pass
    
    def test_repr(self):
        class ConcreteAgent(BaseAgent):
            def check(self, documents, context):
                return []
        
        agent = ConcreteAgent("TestAgent")
        assert "TestAgent" in repr(agent)
