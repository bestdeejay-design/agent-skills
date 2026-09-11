import json
import re
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
                    # Use the level detected from the complete document set. The
                    # previous fallback to L1 made standard audits silently skip
                    # missing L2/L3 documents.
                    detected_level = agent.detect_project_level(result)
                    agent_context["level"] = detected_level
                    all_issues.extend(agent.check_missing(result, detected_level))
                elif isinstance(result, list):
                    all_issues.extend(result)

        # Canon used to be listed in the presets but was never executed. Keep
        # cross-reference checking conservative: only report a contract route
        # absent from all Markdown documents, and label it as a warning because
        # not every route needs prose documentation.
        if preset_name in ("standard", "full"):
            all_issues.extend(self.check_contract_references(documents))

        return all_issues

    def check_contract_references(self, documents: List[Document]) -> List[Issue]:
        """Find obvious OpenAPI routes that are absent from Markdown docs."""
        contracts = [d for d in documents if d.path.endswith((".yaml", ".yml"))]
        markdown = "\n".join(d.content for d in documents if d.path.endswith(".md"))
        issues: List[Issue] = []
        seen = set()
        for contract in contracts:
            for raw in re.findall(r"(?m)^\s{0,4}(/[A-Za-z0-9][A-Za-z0-9_{}./-]*)\s*:", contract.content):
                route = raw.rstrip(":")
                if route in seen or route in markdown:
                    continue
                seen.add(route)
                issues.append(Issue(
                    severity="warning",
                    category="cross_reference",
                    file=contract.path,
                    description=f"Contract route {route} is not mentioned in Markdown documentation",
                    fix=f"Document {route} or mark it intentionally internal",
                ))
        return issues

    def load_preset(self, preset_name: str) -> Dict[str, Any]:
        return PRESETS.get(preset_name, PRESETS["minimal"])
