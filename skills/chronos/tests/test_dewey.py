import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chronos.agents.dewey import Dewey, DOC_PATTERNS, DOC_LEVELS, REQUIRED_DOCS
from chronos.agents.base import Document


class TestDewey:
    def setup_method(self):
        self.dewey = Dewey()
    
    def test_classify_contracts(self):
        docs = [
            Document("/test/contracts/openapi/api.yaml", "openapi: 3.0", 100.0, 50),
        ]
        result = self.dewey.classify(docs)
        assert result["/test/contracts/openapi/api.yaml"] == "contracts"
    
    def test_classify_product_canon(self):
        docs = [
            Document("/test/docs/VISION.md", "# Vision", 100.0, 50),
            Document("/test/docs/PRD.md", "# PRD", 100.0, 50),
        ]
        result = self.dewey.classify(docs)
        assert result["/test/docs/VISION.md"] == "product_canon"
        assert result["/test/docs/PRD.md"] == "product_canon"
    
    def test_classify_engineering_canon(self):
        docs = [
            Document("/test/docs/ARCHITECTURE.md", "# Arch", 100.0, 50),
        ]
        result = self.dewey.classify(docs)
        assert result["/test/docs/ARCHITECTURE.md"] == "engineering_canon"
    
    def test_classify_derived(self):
        docs = [
            Document("/test/README.md", "# README", 100.0, 50),
        ]
        result = self.dewey.classify(docs)
        assert result["/test/README.md"] == "derived"
    
    def test_classify_auxiliary(self):
        docs = [
            Document("/test/LICENSE", "MIT License", 100.0, 50),
            Document("/test/CONTRIBUTING.md", "# Contrib", 100.0, 50),
        ]
        result = self.dewey.classify(docs)
        assert result["/test/LICENSE"] == "auxiliary"
        assert result["/test/CONTRIBUTING.md"] == "auxiliary"
    
    def test_classify_unknown(self):
        docs = [
            Document("/test/random.txt", "content", 100.0, 50),
        ]
        result = self.dewey.classify(docs)
        assert result["/test/random.txt"] == "unknown"
    
    def test_get_relative_path(self):
        assert self.dewey.get_relative_path("/test/docs/VISION.md") == "docs/VISION.md"
        assert self.dewey.get_relative_path("/test/contracts/openapi/api.yaml") == "contracts/openapi/api.yaml"
        assert self.dewey.get_relative_path("/test/README.md") == "README.md"
    
    def test_get_level(self):
        assert self.dewey.get_level("contracts") == 1
        assert self.dewey.get_level("product_canon") == 2
        assert self.dewey.get_level("engineering_canon") == 3
        assert self.dewey.get_level("derived") == 4
        assert self.dewey.get_level("unknown") == 99
    
    def test_detect_project_level_l3(self):
        classification = {"/test/contracts/api.yaml": "contracts", "/test/docs/VISION.md": "product_canon"}
        assert self.dewey.detect_project_level(classification) == "L3"
    
    def test_detect_project_level_l2(self):
        classification = {"/test/docs/VISION.md": "product_canon", "/test/docs/ARCHITECTURE.md": "engineering_canon"}
        assert self.dewey.detect_project_level(classification) == "L2"
    
    def test_detect_project_level_l1(self):
        classification = {"/test/README.md": "derived"}
        assert self.dewey.detect_project_level(classification) == "L1"
    
    def test_check_returns_dict(self):
        docs = [
            Document("/test/docs/VISION.md", "# Vision", 100.0, 50),
        ]
        result = self.dewey.check(docs, {})
        assert isinstance(result, dict)
    
    def test_check_missing_generates_issues(self):
        docs = [
            Document("/test/README.md", "# README", 100.0, 50),
        ]
        classification = self.dewey.classify(docs)
        issues = self.dewey.check_missing(classification, "L2")
        assert len(issues) > 0
        assert all(i.category == "missing" for i in issues)
