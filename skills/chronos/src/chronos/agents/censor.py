import re
from difflib import SequenceMatcher
from typing import List, Dict, Any
from .base import BaseAgent, Issue, Document


class Censor(BaseAgent):
    def __init__(self):
        super().__init__("Censor")
        self.duplicate_threshold = 0.7
    
    def check(self, documents: List[Document], context: Dict[str, Any]) -> List[Issue]:
        issues = []
        issues.extend(self.find_duplicates(documents))
        issues.extend(self.find_broken_links(documents))
        return issues
    
    def find_duplicates(self, documents: List[Document]) -> List[Issue]:
        issues = []
        md_docs = [d for d in documents if d.path.endswith('.md')]
        
        for i, doc1 in enumerate(md_docs):
            for doc2 in md_docs[i+1:]:
                similarity = self.calculate_similarity(doc1.content, doc2.content)
                if similarity >= self.duplicate_threshold:
                    issues.append(Issue(
                        severity="warning",
                        category="duplicate",
                        file=doc1.path,
                        description=f"Высокая схожесть ({similarity:.0%}) с {doc2.path}",
                        related_file=doc2.path,
                        fix="Объединить информацию или оставить только один документ"
                    ))
        
        return issues
    
    def find_broken_links(self, documents: List[Document]) -> List[Issue]:
        issues = []
        
        for doc in documents:
            if not doc.path.endswith('.md'):
                continue
            
            links = self.extract_links(doc.content)
            for link, line in links:
                if link.startswith(('http://', 'https://', '#', 'mailto:')):
                    continue
                
                target = self.resolve_link(doc.path, link)
                if not self.file_exists(target):
                    issues.append(Issue(
                        severity="warning",
                        category="broken_link",
                        file=doc.path,
                        line=line,
                        description=f"Битая ссылка: {link}",
                        fix=f"Создать файл {link} или обновить ссылку"
                    ))
        
        return issues
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        clean1 = re.sub(r'\s+', ' ', text1.strip())
        clean2 = re.sub(r'\s+', ' ', text2.strip())
        return SequenceMatcher(None, clean1, clean2).ratio()
    
    def extract_links(self, content: str) -> List[tuple]:
        links = []
        in_code_block = False
        for line_num, line in enumerate(content.split('\n'), 1):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            clean_line = re.sub(r'`[^`]*`', '', line)
            for match in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', clean_line):
                text, path = match.groups()
                links.append((path, line_num))
        return links
    
    def resolve_link(self, doc_path: str, link: str) -> str:
        from pathlib import Path
        doc_dir = Path(doc_path).parent
        return str((doc_dir / link).resolve())
    
    def file_exists(self, path: str) -> bool:
        from pathlib import Path
        return Path(path).exists()
