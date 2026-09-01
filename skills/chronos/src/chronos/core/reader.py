from pathlib import Path
from typing import List
from ..agents.base import Document


def discover(path: str) -> List[Document]:
    base_path = Path(path)
    documents = []
    
    for md_file in base_path.rglob("*.md"):
        if any(part.startswith('.') for part in md_file.parts):
            continue
        if any(part == 'node_modules' for part in md_file.parts):
            continue
        
        content = read_file(md_file)
        if content is not None:
            stat = md_file.stat()
            documents.append(Document(
                path=str(md_file),
                content=content,
                mtime=stat.st_mtime,
                size=stat.st_size
            ))
    
    contracts_dir = base_path / "contracts"
    if contracts_dir.exists():
        for ext in ("*.yaml", "*.yml"):
            for yaml_file in contracts_dir.rglob(ext):
                content = read_file(yaml_file)
                if content is not None:
                    stat = yaml_file.stat()
                    documents.append(Document(
                        path=str(yaml_file),
                        content=content,
                        mtime=stat.st_mtime,
                        size=stat.st_size
                    ))
    
    return documents


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None
