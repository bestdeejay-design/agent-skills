# Code Review

**Ревью:** `{{REVIEW_TARGET}}`
**Дата:** {{DATE}}
**Найдено замечаний:** {{TOTAL}} (critical: {{CRITICAL}}, warning: {{WARNING}}, nit: {{NIT}})

## Summary

{{SUMMARY}}

## Findings

{{FINDINGS}}

## Checklist

- [ ] Correctness — логика, null/empty, гонки, обработка ошибок
- [ ] Security — SQL-инъекции, секреты, eval, shell, XSS
- [ ] Performance — сложность, аллокации, циклы
- [ ] Style — форматирование, именование, мёртвый код
- [ ] Tests — покрытие новых веток и граничных случаев
- [ ] Edge cases — пустой ввод, границы, деление на ноль

---
*Сгенерировано скиллом `code-review` (MIT © bestdeejay-design).*