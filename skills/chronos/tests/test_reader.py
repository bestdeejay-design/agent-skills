import sys
from pathlib import Path
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chronos.core.reader import discover, read_file


class TestReader:
    def test_discover_finds_md_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "docs").mkdir()
            (Path(tmpdir) / "docs" / "VISION.md").write_text("# Vision")
            (Path(tmpdir) / "docs" / "PRD.md").write_text("# PRD")
            (Path(tmpdir) / "README.md").write_text("# README")
            
            docs = discover(tmpdir)
            assert len(docs) == 3
            paths = [d.path for d in docs]
            assert any("VISION.md" in p for p in paths)
            assert any("PRD.md" in p for p in paths)
            assert any("README.md" in p for p in paths)
    
    def test_discover_ignores_hidden_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".git").mkdir()
            (Path(tmpdir) / ".git" / "config.md").write_text("# Git config")
            (Path(tmpdir) / "README.md").write_text("# README")
            
            docs = discover(tmpdir)
            assert len(docs) == 1
    
    def test_discover_ignores_node_modules(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "node_modules").mkdir()
            (Path(tmpdir) / "node_modules" / "pkg").mkdir()
            (Path(tmpdir) / "node_modules" / "pkg" / "README.md").write_text("# Pkg")
            (Path(tmpdir) / "README.md").write_text("# README")
            
            docs = discover(tmpdir)
            assert len(docs) == 1
    
    def test_discover_finds_yaml_in_contracts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "contracts").mkdir()
            (Path(tmpdir) / "contracts" / "openapi.yaml").write_text("openapi: 3.0")
            (Path(tmpdir) / "contracts" / "asyncapi.yml").write_text("asyncapi: 2.0")
            
            docs = discover(tmpdir)
            assert len(docs) == 2
    
    def test_discover_finds_yml_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "contracts").mkdir()
            (Path(tmpdir) / "contracts" / "api.yml").write_text("openapi: 3.0")
            
            docs = discover(tmpdir)
            assert len(docs) == 1
    
    def test_read_file_success(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test content")
            f.flush()
            content = read_file(Path(f.name))
            os.unlink(f.name)
            assert content == "# Test content"
    
    def test_read_file_nonexistent(self):
        content = read_file(Path("/nonexistent/file.md"))
        assert content is None
    
    def test_discover_populates_document_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.md").write_text("# Test")
            docs = discover(tmpdir)
            assert len(docs) == 1
            doc = docs[0]
            assert doc.path.endswith("test.md")
            assert doc.content == "# Test"
            assert doc.size > 0
            assert doc.mtime > 0
