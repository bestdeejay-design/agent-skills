from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class Issue:
    severity: str
    category: str
    file: str
    description: str
    line: Optional[int] = None
    related_file: Optional[str] = None
    fix: str = ""


@dataclass
class Document:
    path: str
    content: str
    mtime: float
    size: int


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def check(self, documents: List[Document], context: Dict[str, Any]) -> List[Issue]:
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
