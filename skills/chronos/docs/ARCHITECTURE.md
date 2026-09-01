# ARCHITECTURE — Docs Pantheon

> Как устроен технически

## Overview

Docs Pantheon — модульная система AI-агентов для проверки документации. Каждый агент — отдельный модуль с чёткой зоной ответственности. Оркестратор (Canon) координирует цепочку.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI LAYER                           │
│  python3 -m chronos --path . --preset full            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                           │
│                        (Canon)                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. Load preset (minimal/standard/full)              │   │
│  │ 2. Create agent instances                           │   │
│  │ 3. Run chain: Dewey → Veles → Censor → Chronos     │   │
│  │ 4. Aggregate results                                │   │
│  │ 5. Generate report                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      CORE MODULES                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Reader     │  │ Classifier   │  │   Reporter   │     │
│  │              │  │              │  │              │     │
│  │ • Glob .md   │  │ • Patterns   │  │ • JSON       │     │
│  │ • Read YAML  │  │ • Rules      │  │ • Markdown   │     │
│  │ • Exclude    │  │ • Tree       │  │ • Summary    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                        AGENTS                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ Dewey   │  │ Veles   │  │ Censor  │  │ Chronos │      │
│  │         │  │         │  │         │  │         │      │
│  │Classify │  │ Count   │  │ Check   │  │ Time    │      │
│  │ Index   │  │ Links   │  │ Facts   │  │ Stale   │      │
│  │ Tree    │  │ Orphans │  │ Dups    │  │ Archive │      │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Step 1: Discovery (Reader)

```python
# Вход: путь к проекту
# Выход: List[Document]

def discover(path: Path) -> List[Document]:
    documents = []
    
    # 1. Найти все .md файлы
    for md_file in path.rglob("*.md"):
        if not is_hidden(md_file):
            content = read_file(md_file)
            documents.append(Document(path=md_file, content=content))
    
    # 2. Найти YAML контракты
    for yaml_file in path.rglob("*.yaml"):
        if "contracts" in yaml_file.parts:
            content = read_file(yaml_file)
            documents.append(Document(path=yaml_file, content=content))
    
    return documents
```

### Step 2: Classification (Dewey)

```python
# Вход: List[Document]
# Выход: Dict[Document, DocType]

def classify(documents: List[Document]) -> Dict[Document, DocType]:
    classification = {}
    
    for doc in documents:
        # Определить тип по паттерну пути
        doc_type = match_pattern(doc.path)
        
        # Построить зависимости (ссылки)
        links = extract_links(doc.content)
        
        classification[doc] = ClassifiedDocument(
            type=doc_type,
            level=get_level(doc_type),
            links=links
        )
    
    return classification
```

### Step 3: Analysis (Veles)

```python
# Вход: Dict[Document, DocType]
# Выход: Stats

def analyze(classification: Dict[Document, DocType]) -> Stats:
    stats = Stats()
    
    # 1. Подсчитать документы по типам
    for doc, doc_type in classification.items():
        stats.count_by_type[doc_type] += 1
    
    # 2. Найти сирот (документы без ссылок)
    all_links = collect_all_links(classification)
    for doc in classification:
        if doc.path not in all_links:
            stats.orphans.append(doc)
    
    # 3. Построить граф зависимостей
    stats.dependency_graph = build_graph(classification)
    
    return stats
```

### Step 4: Verification (Censor)

```python
# Вход: Dict[Document, DocType>, Stats
# Выход: List[Issue]

def verify(classification, stats) -> List[Issue]:
    issues = []
    
    # 1. Дубликаты
    duplicates = find_duplicates(classification)
    issues.extend(duplicates)
    
    # 2. Противоречия
    contradictions = find_contradictions(classification)
    issues.extend(contradictions)
    
    # 3. Битые ссылки
    broken_links = find_broken_links(classification)
    issues.extend(broken_links)
    
    # 4. Пропущенные документы
    missing = find_missing(classification)
    issues.extend(missing)
    
    return issues
```

### Step 5: Temporal (Chronos)

```python
# Вход: Dict[Document, DocType>
# Выход: List[Issue]

def check_time(classification) -> List[Issue]:
    issues = []
    
    for doc in classification:
        # 1. Проверить модификацию
        mtime = get_modification_time(doc)
        
        # 2. Сравнить с зависимостями
        for dep in doc.links:
            if dep.mtime > mtime:
                issues.append(Issue(
                    severity="warning",
                    category="stale",
                    file=doc.path,
                    description=f"Зависимость {dep} обновлена позже"
                ))
        
        # 3. Проверить срок годности
        if is_archive_candidate(doc):
            issues.append(Issue(
                severity="info",
                category="archive",
                file=doc.path,
                description="Кандидат в архив"
            ))
    
    return issues
```

### Step 6: Orchestration (Canon)

```python
# Вход: все результаты
# Выход: Report

def orchestrate(path, preset):
    # 1. Загрузить пресет
    agents = load_preset(preset)
    
    # 2. Discovery
    documents = discover(path)
    
    # 3. Classification
    classification = classify(documents)
    
    # 4. Analysis
    stats = analyze(classification)
    
    # 5. Verification
    issues = []
    
    if "censor" in agents:
        issues.extend(verify(classification, stats))
    
    if "chronos" in agents:
        issues.extend(check_time(classification))
    
    # 6. Generate report
    return Report(
        meta=Meta(path=path, level=detect_level(classification)),
        classification=classification,
        stats=stats,
        issues=issues
    )
```

## Data Models

### Document

```python
@dataclass
class Document:
    path: Path
    content: str
    mtime: float
    size: int
```

### DocType

```python
class DocType(Enum):
    CONTRACTS = "contracts"           # L1
    PRODUCT_CANON = "product_canon"   # L2
    ENGINEERING_CANON = "engineering_canon"  # L3
    DERIVED = "derived"               # L4
    ARTIFACTS = "artifacts"           # L5
    AUXILIARY = "auxiliary"            # L6
    UNKNOWN = "unknown"
```

### Issue

```python
@dataclass
class Issue:
    severity: str      # critical, warning, nit
    category: str      # duplicate, contradiction, broken_link, orphan, missing, stale
    file: str
    line: Optional[int]
    description: str
    related_file: Optional[str]
    fix: str
```

### Report

```python
@dataclass
class Report:
    meta: Meta
    classification: Dict[Document, DocType]
    stats: Stats
    issues: List[Issue]
    recommendations: List[Recommendation]
```

## Presets

### Minimal

```json
{
  "name": "minimal",
  "agents": ["censor"],
  "checks": ["duplicates", "broken_links", "missing"]
}
```

### Standard

```json
{
  "name": "standard",
  "agents": ["censor", "dewey", "canon"],
  "checks": ["duplicates", "broken_links", "missing", "orphan", "classification"]
}
```

### Full

```json
{
  "name": "full",
  "agents": ["censor", "dewey", "veles", "chronos", "canon"],
  "checks": ["all"]
}
```

## File Structure

```
chronos/
├── docs/
│   ├── VISION.md
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── FEATURES.md
│   ├── STATUS.md
│   └── REFERENCE.md
├── src/
│   └── chronos/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── reader.py
│       │   ├── classifier.py
│       │   └── reporter.py
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── censor.py
│       │   ├── dewey.py
│       │   ├── veles.py
│       │   ├── chronos.py
│       │   └── canon.py
│       └── cli.py
├── presets/
│   ├── minimal.json
│   ├── standard.json
│   └── full.json
├── tests/
│   ├── test_reader.py
│   ├── test_classifier.py
│   └── test_agents.py
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── CHANGELOG.md
```

## Dependencies

### Core (stdlib only)
- `argparse` — CLI
- `json` — отчёты
- `pathlib` — пути
- `re` — регулярки
- `hashlib` — хеши
- `difflib` — сравнение текстов
- `dataclasses` — модели данных

### Optional (dev)
- `pytest` — тесты
- `black` — форматирование
- `mypy` — типизация

## Performance

| Operation | Complexity | Target |
|-----------|------------|--------|
| Discovery | O(n) | < 1s |
| Classification | O(n) | < 1s |
| Duplicate detection | O(n²) | < 10s |
| Link checking | O(n × m) | < 5s |
| **Total** | O(n²) | < 30s |

Where n = number of documents, m = average links per document.

---

*Architecture created: 2026-09-01*
*Author: best*
