import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chronos.agents.veles import Veles
from chronos.agents.base import Document


class TestVeles:
    def setup_method(self):
        self.veles = Veles()
    
    def test_collect_all_links(self):
        docs = [
            Document("/test/a.md", "[link](b.md)", 100.0, 50),
            Document("/test/b.md", "# B", 100.0, 50),
        ]
        links = self.veles.collect_all_links(docs)
        assert "b.md" in links
        assert "/test/a.md" in links["b.md"]
    
    def test_collect_all_links_skips_http(self):
        docs = [
            Document("/test/a.md", "[link](https://example.com)", 100.0, 50),
        ]
        links = self.veles.collect_all_links(docs)
        assert len(links) == 0
    
    def test_collect_all_links_skips_code_blocks(self):
        docs = [
            Document("/test/a.md", "```\n[link](b.md)\n```\n[real](c.md)", 100.0, 50),
        ]
        links = self.veles.collect_all_links(docs)
        assert "b.md" not in links
        assert "c.md" in links
    
    def test_find_orphans(self):
        docs = [
            Document("/test/a.md", "[link](b.md)", 100.0, 50),
            Document("/test/b.md", "# B", 100.0, 50),
            Document("/test/c.md", "# C", 100.0, 50),
        ]
        links = self.veles.collect_all_links(docs)
        orphans = self.veles.find_orphans(docs, links)
        assert "/test/c.md" in orphans
        assert "/test/b.md" not in orphans
    
    def test_find_orphans_empty(self):
        docs = [
            Document("/test/a.md", "# A", 100.0, 50),
        ]
        links = {}
        orphans = self.veles.find_orphans(docs, links)
        assert len(orphans) == 1
    
    def test_compute_stats(self):
        classification = {
            "/test/a.md": "product_canon",
            "/test/b.md": "product_canon",
            "/test/c.md": "engineering_canon",
        }
        orphans = ["/test/c.md"]
        stats = self.veles.compute_stats(classification, orphans)
        assert stats["total_docs"] == 3
        assert stats["by_type"]["product_canon"] == 2
        assert stats["orphan_count"] == 1
    
    def test_check_integration(self):
        docs = [
            Document("/test/a.md", "[link](b.md)", 100.0, 50),
            Document("/test/b.md", "# B", 100.0, 50),
            Document("/test/c.md", "# C", 100.0, 50),
        ]
        issues = self.veles.check(docs, {})
        assert isinstance(issues, list)
        assert len(issues) >= 1
        assert all(i.category == "orphan" for i in issues)
