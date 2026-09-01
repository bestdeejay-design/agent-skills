import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from .base import BaseAgent, Issue, Document


class Chronos(BaseAgent):
    def __init__(self):
        super().__init__("Chronos")
    
    def check(self, documents: List[Document], context: Dict[str, Any]) -> List[Issue]:
        return self.check_staleness(documents, context)
    
    def check_staleness(self, documents: List[Document], context: Dict[str, Any]) -> List[Issue]:
        issues = []
        classification = context.get("classification", {})
        
        for doc in documents:
            if not doc.path.endswith('.md'):
                continue
            
            doc_type = classification.get(doc.path, "unknown")
            if doc_type in ("contracts", "auxiliary", "artifacts"):
                continue
            
            links = self.extract_links(doc.content)
            for link in links:
                target_doc = self.find_target(doc.path, link, documents)
                if target_doc and target_doc.mtime > doc.mtime:
                    issues.append(Issue(
                        severity="warning",
                        category="stale",
                        file=doc.path,
                        description=f"Зависимость {link} обновлена позже документа",
                        related_file=target_doc.path,
                        fix=f"Обновить {doc.path} после изменений в {link}"
                    ))
        
        return issues
    
    def extract_links(self, content: str) -> List[str]:
        links = []
        in_code_block = False
        for line in content.split('\n'):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            clean_line = re.sub(r'`[^`]*`', '', line)
            for match in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', clean_line):
                text, path = match.groups()
                if not path.startswith(('http://', 'https://', '#', 'mailto:')):
                    links.append(path)
        return links
    
    def find_target(self, source_path: str, link: str, documents: List[Document]) -> Optional[Document]:
        source_dir = Path(source_path).parent
        target = (source_dir / link).resolve()
        
        for doc in documents:
            if Path(doc.path).resolve() == target:
                return doc
        
        return None
