import json
from pathlib import Path
from typing import List, Dict, Any
from .base import BaseAgent, Issue, Document
from .censor import Censor
from .dewey import Dewey
from .veles import Veles
from .chronos import Chronos


PRESETS = {
    "minimal": {
        "name": "minimal",
        "agents": ["censor"],
        "description": "Базовый аудит: дубли, битые ссылки"
    },
    "standard": {
        "name": "standard",
        "agents": ["censor", "dewey", "canon"],
        "description": "Полная проверка + классификация"
    },
    "full": {
        "name": "full",
        "agents": ["censor", "dewey", "veles", "chronos", "canon"],
        "description": "Полный Пантеон"
    }
}


class Canon(BaseAgent):
    def __init__(self):
        super().__init__("Canon")
        self.agents = {
            "censor": Censor(),
            "dewey": Dewey(),
            "veles": Veles(),
            "chronos": Chronos(),
        }
    
    def check(self, documents: List[Document], context: Dict[str, Any]) -> List[Issue]:
        return self.orchestrate(documents, context)
    
    def orchestrate(self, documents: List[Document], context: Dict[str, Any]) -> List[Issue]:
        preset_name = context.get("preset", "minimal")
        preset = PRESETS.get(preset_name, PRESETS["minimal"])
        
        all_issues: List[Issue] = []
        agent_context = dict(context)
        
        for agent_name in preset["agents"]:
            if agent_name == "canon":
                continue
            
            agent = self.agents.get(agent_name)
            if agent:
                result = agent.check(documents, agent_context)
                
                if agent_name == "dewey" and isinstance(result, dict):
                    agent_context["classification"] = result
                    classification_issues = agent.check_missing(result, agent_context.get("level", "L1"))
                    all_issues.extend(classification_issues)
                elif isinstance(result, list):
                    all_issues.extend(result)
        
        return all_issues
    
    def load_preset(self, preset_name: str) -> Dict[str, Any]:
        return PRESETS.get(preset_name, PRESETS["minimal"])
