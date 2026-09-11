# Chronos configuration reference

The CLI currently accepts these arguments:

```text
--path PATH                 project root, default '.'
--preset minimal|standard|full
--output json|markdown|both
--output-file PATH
--fail-on critical|warning|nit
```

`minimal` runs duplicate/link checks. `standard` adds classification and
required-document checks. `full` adds staleness analysis and contract-route
cross-reference warnings.

Exit status is `0` when no selected threshold is reached, `1` when
`--fail-on` is triggered, and `2` for invalid or missing project paths.
