import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chronos.agents.censor import Censor
from chronos.agents.base import Document


class TestCensor:
    def setup_method(self):
        self.censor = Censor()
    
    def test_find_duplicates_identical(self):
        docs = [
            Document("/test/a.md", "# Title\n\nContent here.", 100.0, 50),
            Document("/test/b.md", "# Title\n\nContent here.", 100.0, 50),
        ]
        issues = self.censor.find_duplicates(docs)
        assert len(issues) == 1
        assert issues[0].category == "duplicate"
        assert "100%" in issues[0].description
    
    def test_find_duplicates_similar(self):
        docs = [
            Document("/test/a.md", "# API\n\nGet users endpoint.", 100.0, 50),
            Document("/test/b.md", "# API\n\nGet user endpoint.", 100.0, 50),
        ]
        issues = self.censor.find_duplicates(docs)
        assert len(issues) >= 1
    
    def test_find_duplicates_different(self):
        docs = [
            Document("/test/a.md", "# API Reference", 100.0, 50),
            Document("/test/b.md", "# Contributing Guide", 100.0, 50),
        ]
        issues = self.censor.find_duplicates(docs)
        assert len(issues) == 0
    
    def test_extract_links(self):
        content = "# Title\n\n[link](file.md)\n\n`[not a link](fake.md)`\n\n[another](doc.md)"
        links = self.censor.extract_links(content)
        assert len(links) == 2
        assert links[0] == ("file.md", 3)
        assert links[1] == ("doc.md", 7)
    
    def test_extract_links_in_code_block(self):
        content = "# Title\n\n```\n[link](file.md)\n```\n\n[real](doc.md)"
        links = self.censor.extract_links(content)
        assert len(links) == 1
        assert links[0] == ("doc.md", 7)
    
    def test_extract_links_skips_http(self):
        issues = self.censor.find_broken_links([
            Document("/test/a.md", "[link](https://example.com)", 100.0, 50),
        ])
        assert len(issues) == 0
    
    def test_find_broken_links(self):
        issues = self.censor.find_broken_links([
            Document("/test/a.md", "[link](nonexistent.md)", 100.0, 50),
        ])
        assert len(issues) == 1
        assert issues[0].category == "broken_link"
    
    def test_find_broken_links_skips_code_blocks(self):
        issues = self.censor.find_broken_links([
            Document("/test/a.md", "```\n[link](fake.md)\n```", 100.0, 50),
        ])
        assert len(issues) == 0
    
    def test_check_integration(self):
        docs = [
            Document("/test/a.md", "# Title\n\nContent.", 100.0, 50),
            Document("/test/b.md", "# Different", 100.0, 50),
        ]
        issues = self.censor.check(docs, {})
        assert isinstance(issues, list)
