import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chronos.agents.chronos import Chronos
from chronos.agents.base import Document


class TestChronos:
    def setup_method(self):
        self.chronos = Chronos()
    
    def test_extract_links(self):
        content = "# Title\n\n[link](file.md)\n\n`[not a link](fake.md)`\n\n[another](doc.md)"
        links = self.chronos.extract_links(content)
        assert len(links) == 2
        assert "file.md" in links
        assert "doc.md" in links
    
    def test_extract_links_skips_http(self):
        content = "[link](https://example.com)\n[local](file.md)"
        links = self.chronos.extract_links(content)
        assert len(links) == 1
        assert "file.md" in links
    
    def test_extract_links_skips_code_blocks(self):
        content = "```\n[link](file.md)\n```\n[real](doc.md)"
        links = self.chronos.extract_links(content)
        assert len(links) == 1
        assert "doc.md" in links
    
    def test_find_target_found(self):
        now = time.time()
        docs = [
            Document("/test/main.md", "[link](sub/file.md)", now, 50),
            Document("/test/sub/file.md", "# File", now, 50),
        ]
        target = self.chronos.find_target("/test/main.md", "sub/file.md", docs)
        assert target is not None
        assert target.path == "/test/sub/file.md"
    
    def test_find_target_not_found(self):
        docs = [
            Document("/test/main.md", "[link](missing.md)", 100.0, 50),
        ]
        target = self.chronos.find_target("/test/main.md", "missing.md", docs)
        assert target is None
    
    def test_staleness_detected(self):
        old_time = 1000.0
        new_time = 2000.0
        docs = [
            Document("/test/main.md", "[link](dep.md)", old_time, 50),
            Document("/test/dep.md", "# Dep", new_time, 50),
        ]
        issues = self.chronos.check_staleness(docs, {})
        assert len(issues) == 1
        assert issues[0].category == "stale"
        assert issues[0].related_file == "/test/dep.md"
    
    def test_staleness_not_detected(self):
        old_time = 1000.0
        newer_time = 2000.0
        docs = [
            Document("/test/main.md", "[link](dep.md)", newer_time, 50),
            Document("/test/dep.md", "# Dep", old_time, 50),
        ]
        issues = self.chronos.check_staleness(docs, {})
        assert len(issues) == 0
    
    def test_staleness_skips_contracts(self):
        now = time.time()
        docs = [
            Document("/test/main.md", "[link](contracts/api.yaml)", now + 100, 50),
        ]
        issues = self.chronos.check_staleness(docs, {"classification": {"/test/main.md": "contracts"}})
        assert len(issues) == 0
    
    def test_staleness_uses_classification(self):
        old_time = 1000.0
        new_time = 2000.0
        docs = [
            Document("/test/main.md", "[link](dep.md)", old_time, 50),
            Document("/test/dep.md", "# Dep", new_time, 50),
        ]
        classification = {"/test/main.md": "contracts"}
        issues = self.chronos.check_staleness(docs, {"classification": classification})
        assert len(issues) == 0
    
    def test_check_integration(self):
        docs = [
            Document("/test/main.md", "[link](dep.md)", 1000.0, 50),
            Document("/test/dep.md", "# Dep", 2000.0, 50),
        ]
        issues = self.chronos.check(docs, {})
        assert isinstance(issues, list)
        assert len(issues) == 1
