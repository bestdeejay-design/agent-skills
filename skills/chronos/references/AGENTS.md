# Chronos agent contract

Each agent receives a list of `Document` objects and a context dictionary. An
agent returns either a list of `Issue` objects or, for Dewey, a classification
mapping that Canon turns into issues.

Every issue should include:

- `severity`: `critical`, `warning`, or `info`;
- `category`: stable machine-readable category;
- `file`: repository-relative or supplied document path;
- `description`: evidence-based explanation;
- `fix`: a concrete remediation, when one is possible;
- `line` or `related_file` when the detector can determine them.

Agents must be deterministic for the same input. They must not rewrite project
files during an audit. The CLI owns formatting and exit status.
