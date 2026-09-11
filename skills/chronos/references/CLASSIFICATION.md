# Chronos classification reference

Chronos uses a practical six-level documentation taxonomy:

| Level | Meaning | Typical evidence |
|---|---|---|
| L1 | Machine contracts | OpenAPI, AsyncAPI, JSON Schema |
| L2 | Product canon | Vision, PRD, roadmap, features |
| L3 | Engineering canon | Architecture, ADR, SAGA, test cases |
| L4 | Derived guidance | Reference map, developer guide, status |
| L5 | Generated artifacts | API docs, changelog, diagrams |
| L6 | Auxiliary project docs | README, contributing, license, templates |

Classification is a routing aid, not a claim that every repository must contain
all six levels. Missing-document findings should be interpreted against the
project's detected maturity and explicitly configured requirements.
