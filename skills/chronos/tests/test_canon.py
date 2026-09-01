import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chronos.agents.canon import Canon, PRESETS
from chronos.agents.base import Document, Issue


class TestCanon:
    def setup_method(self):
        self.canon = Canon()
    
    def test_presets_defined(self):
        assert "minimal" in PRESETS
        assert "standard" in PRESETS
        assert "full" in PRESETS
    
    def test_minimal_has_censor(self):
        assert "censor" in PRESETS["minimal"]["agents"]
    
    def test_standard_has_censor_dewey(self):
        agents = PRESETS["standard"]["agents"]
        assert "censor" in agents
        assert "dewey" in agents
    
    def test_full_has_all(self):
        agents = PRESETS["full"]["agents"]
        assert "censor" in agents
        assert "dewey" in agents
        assert "veles" in agents
        assert "chronos" in agents
    
    def test_load_preset(self):
        assert self.canon.load_preset("minimal") == PRESETS["minimal"]
        assert self.canon.load_preset("nonexistent") == PRESETS["minimal"]
    
    def test_orchestrate_minimal(self):
        docs = [
            Document("/test/a.md", "# A\n\n[link](b.md)", 100.0, 50),
            Document("/test/b.md", "# B", 100.0, 50),
        ]
        issues = self.canon.orchestrate(docs, {"preset": "minimal"})
        assert isinstance(issues, list)
        for issue in issues:
            assert isinstance(issue, Issue)
    
    def test_orchestrate_full(self):
        docs = [
            Document("/test/README.md", "# README", 100.0, 50),
            Document("/test/docs/VISION.md", "# Vision", 100.0, 50),
        ]
        issues = self.canon.orchestrate(docs, {"preset": "full"})
        assert isinstance(issues, list)
        for issue in issues:
            assert isinstance(issue, Issue)
    
    def test_orchestrate_returns_only_issues(self):
        docs = [
            Document("/test/a.md", "# A", 100.0, 50),
        ]
        issues = self.canon.orchestrate(docs, {"preset": "full"})
        for issue in issues:
            assert not isinstance(issue, str), f"Got string in issues: {issue}"
            assert isinstance(issue, Issue)
    
    def test_check_same_as_orchestrate(self):
        docs = [
            Document("/test/a.md", "# A", 100.0, 50),
        ]
        issues = self.canon.check(docs, {"preset": "minimal"})
        assert isinstance(issues, list)
