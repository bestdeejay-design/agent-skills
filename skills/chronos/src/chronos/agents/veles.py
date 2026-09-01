import re
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseAgent, Issue, Document


class Veles(BaseAgent):
    def __init__(self):
        super().__init__("Veles")
    
    def check(self, documents: List[Document], context: Dict[str, Any]) -> List[Issue]:
        analysis = self.analyze(documents, context)
        return analysis.get("issues", [])
    
    def analyze(self, documents: List[Document], context: Dict[str, Any]) -> Dict[str, Any]:
        classification = context.get("classification", {})
        all_links = self.collect_all_links(documents)
        orphans = self.find_orphans(documents, all_links)
        stats = self.compute_stats(classification, orphans)
        
        issues = []
        for orphan in orphans:
            issues.append(Issue(
                severity="nit",
                category="orphan",
                file=orphan,
                description="Документ без ссылок на него",
                fix="Добавить ссылку в REFERENCE.md или удалить"
            ))
        
        return {
            "stats": stats,
            "orphans": orphans,
            "issues": issues
        }
    
    def collect_all_links(self, documents: List[Document]) -> Dict[str, List[str]]:
        link_targets = defaultdict(list)
        
        for doc in documents:
            if not doc.path.endswith('.md'):
                continue
            
            in_code_block = False
            for line in doc.content.split('\n'):
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue
                clean_line = re.sub(r'`[^`]*`', '', line)
                for match in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', clean_line):
                    text, path = match.groups()
                    if not path.startswith(('http://', 'https://', '#', 'mailto:')):
                        link_targets[path].append(doc.path)
        
        return dict(link_targets)
    
    def find_orphans(self, documents: List[Document], all_links: Dict[str, List[str]]) -> List[str]:
        orphans = []
        
        for doc in documents:
            if not doc.path.endswith('.md'):
                continue
            
            is_linked = False
            doc_path = Path(doc.path)
            
            for target in all_links.keys():
                try:
                    target_resolved = (doc_path.parent / target).resolve()
                    if doc_path.resolve() == target_resolved:
                        is_linked = True
                        break
                except Exception:
                    continue
            
            if not is_linked:
                orphans.append(doc.path)
        
        return orphans
    
    def compute_stats(self, classification: Dict[str, str], orphans: List[str]) -> Dict[str, Any]:
        type_counts = defaultdict(int)
        for doc_type in classification.values():
            type_counts[doc_type] += 1
        
        return {
            "total_docs": len(classification),
            "by_type": dict(type_counts),
            "orphan_count": len(orphans)
        }
