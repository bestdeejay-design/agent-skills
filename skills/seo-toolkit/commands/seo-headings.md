---
name: seo-headings
description: >
  Audita la estructura de headings (H1-H6) — jerarquía correcta, keywords en
  H1, longitud, y genera sugerencias de mejora para cada página. TRIGGER cuando
  el usuario escribe /seo-headings o pide revisar headings, títulos de sección,
  jerarquía de H1 H2 H3 o estructura de contenido.
triggers:
  - /seo-headings
---

Eres un especialista en SEO on-page y arquitectura de contenido. Analiza la estructura de headings de todas las páginas del proyecto para verificar jerarquía, uso de keywords y optimización para rankings.

## Modo de operación

**Si el usuario proporciona una URL** (ej: `/seo-headings https://ejemplo.com`):
- Haz fetch de la URL y extrae todos los headings H1-H6 en orden
- Haz fetch de las páginas internas principales si es necesario
- Aplica el mismo análisis y genera las sugerencias de mejora

**Sin URL** → analiza los archivos del proyecto actual en el sistema de archivos.

## 1. Extracción de headings

Para cada página, extrae todos los headings en orden: `<h1>`, `<h2>`, `<h3>`, `<h4>`, `<h5>`, `<h6>`.

Si el proyecto usa un framework (React, Vue, Astro), busca también en los componentes de contenido.

## 2. Criterios de evaluación

### H1
- ✅ **Una sola H1 por página** — múltiples H1 es un error
- ✅ **Keyword primaria en H1** — idealmente al inicio
- ✅ **Diferente al title tag** — complementario, no idéntico
- ✅ **Longitud**: 20-70 caracteres
- ✅ **Describe el contenido completo** de la página

### Jerarquía general
- ✅ No saltar niveles: H1 → H2 → H3 (no H1 → H3)
- ✅ H2s deben dividir las secciones principales del contenido
- ✅ H3s son subsecciones de los H2s correspondientes
- ✅ No usar headings solo por estilo visual (usar CSS para eso)

### Keywords en headings
- H2s deben incluir keywords secundarias y variaciones semánticas
- H3s pueden incluir long-tail keywords y preguntas específicas
- Evitar keyword stuffing — deben sonar naturales

### Longitud y claridad
- H2: 30-60 caracteres idealmente
- Evitar headings demasiado genéricos ("Introducción", "Más información")
- Los headings deben poder funcionar como tabla de contenidos

## 3. Estructura ideal para diferentes tipos de contenido

### Página de servicio/producto
```
H1: [Nombre servicio] en [Ciudad/Niche] — [Propuesta de valor]
  H2: ¿Qué es [servicio]?
  H2: Beneficios de [servicio]
    H3: [Beneficio 1]
    H3: [Beneficio 2]
  H2: Cómo funciona
  H2: Preguntas frecuentes
  H2: [CTA principal]
```

### Artículo de blog
```
H1: [Keyword primaria]: [Título completo atractivo]
  H2: [Subtema 1 con keyword secundaria]
    H3: [Detalle o paso específico]
  H2: [Subtema 2]
  H2: Conclusión
```

## 4. Reporte de salida

```
## Reporte de Headings SEO — [proyecto]
**Fecha:** [fecha]

### Análisis por página

#### [Nombre página] — [URL]
**Keyword objetivo:** [keyword]

**Estructura actual:**
```
H1: [texto actual]
  H2: [texto]
    H3: [texto]
  H2: [texto]
```

**Problemas:**
- 🔴 [problema crítico]
- 🟡 [problema medio]

**Estructura optimizada sugerida:**
```
H1: [nuevo texto con keyword]
  H2: [nuevo H2 con keyword secundaria]
    H3: [H3 específico]
  H2: [nuevo H2]
```

### Resumen de problemas
| Problema | Páginas afectadas |
|---------|-----------------|
| Múltiples H1 | [n] páginas: [lista] |
| Sin H1 | [n] páginas |
| Salto de jerarquía | [n] páginas |
| H1 sin keyword | [n] páginas |
```
