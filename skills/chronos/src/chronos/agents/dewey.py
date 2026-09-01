import re
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseAgent, Document


DOC_PATTERNS = {
    "contracts": [
        r"contracts/openapi/.*\.ya?ml$",
        r"contracts/asyncapi/.*\.ya?ml$",
    ],
    "product_canon": [
        r"docs/VISION\.md$",
        r"docs/PRD\.md$",
        r"docs/ROADMAP\.md$",
    ],
    "engineering_canon": [
        r"docs/ARCHITECTURE\.md$",
        r"docs/ADR/ADR-\d+\.md$",
        r"docs/SAGA\.md$",
        r"docs/TEST_CASES\.md$",
        r"docs/DECISIONS\.md$",
    ],
    "derived": [
        r"^README\.md$",
        r"^ENTRY\.md$",
        r"docs/STATUS\.md$",
        r"docs/REFERENCE\.md$",
        r"docs/FEATURES\.md$",
    ],
    "auxiliary": [
        r"^LICENSE$",
        r"^CONTRIBUTING\.md$",
        r"^CODE_OF_CONDUCT\.md$",
        r"^SECURITY\.md$",
    ],
}

DOC_LEVELS = {
    "contracts": 1,
    "product_canon": 2,
    "engineering_canon": 3,
    "derived": 4,
    "artifacts": 5,
    "auxiliary": 6,
}

REQUIRED_DOCS = {
    "L1": ["README.md", "docs/ARCHITECTURE.md"],
    "L2": ["docs/VISION.md", "docs/PRD.md", "docs/ROADMAP.md", "docs/REFERENCE.md"],
    "L3": ["contracts/", "docs/SAGA.md", "docs/TEST_CASES.md"],
}


class Dewey(BaseAgent):
    def __init__(self):
        super().__init__("Dewey")
    
    def check(self, documents: List[Document], context: Dict[str, Any]):
        return self.classify(documents)
    
    def classify(self, documents: List[Document]) -> Dict[str, str]:
        classification = {}
        for doc in documents:
            rel_path = self.get_relative_path(doc.path)
            doc_type = self.match_type(rel_path)
            classification[doc.path] = doc_type
        return classification
    
    def get_relative_path(self, path: str) -> str:
        parts = Path(path).parts
        for i, part in enumerate(parts):
            if part == "docs":
                return "/".join(parts[i:])
            if part == "contracts":
                return "/".join(parts[i:])
        return Path(path).name
    
    def match_type(self, rel_path: str) -> str:
        for doc_type, patterns in DOC_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, rel_path):
                    return doc_type
        return "unknown"
    
    def get_level(self, doc_type: str) -> int:
        return DOC_LEVELS.get(doc_type, 99)
    
    def detect_project_level(self, classification: Dict[str, str]) -> str:
        types_found = set(classification.values())
        if "contracts" in types_found:
            return "L3"
        if "product_canon" in types_found and "engineering_canon" in types_found:
            return "L2"
        return "L1"
    
    def check_missing(self, classification: Dict[str, str], project_level: str) -> List:
        from .base import Issue
        issues = []
        types_found = set(classification.values())
        
        for level in ["L1", "L2", "L3"]:
            if project_level == "L1" and level in ["L2", "L3"]:
                continue
            if project_level == "L2" and level == "L3":
                continue
            
            for doc in REQUIRED_DOCS.get(level, []):
                if doc.endswith("/"):
                    if not any(d.startswith(doc) for d in classification.keys()):
                        issues.append(Issue(
                            severity="warning",
                            category="missing",
                            file=doc,
                            description=f"Отсутствует обязательная директория для {level}",
                            fix=f"Создать {doc}"
                        ))
                else:
                    if not any(d.endswith(doc) or d.endswith(doc.replace("docs/", "")) for d in classification.keys()):
                        issues.append(Issue(
                            severity="warning",
                            category="missing",
                            file=doc,
                            description=f"Отсутствует обязательный документ для {level}",
                            fix=f"Создать {doc}"
                        ))
        
        return issues
