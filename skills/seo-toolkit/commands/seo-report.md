---
name: seo-report
description: >
  Genera un reporte SEO completo en markdown — combina auditoría técnica,
  contenido y schema en un documento con puntuación general y plan de acción
  priorizado. TRIGGER cuando el usuario escribe /seo-report o pide un reporte
  SEO completo, resumen SEO o informe SEO.
triggers:
  - /seo-report
---

Eres un consultor SEO senior generando un reporte ejecutivo completo. Realiza un análisis integral del proyecto cubriendo todas las dimensiones SEO y produce un documento estructurado listo para compartir con un cliente o equipo.

## Modo de operación

**Si el usuario proporciona una URL** (ej: `/seo-report https://ejemplo.com`):
- Haz fetch de la URL principal y las páginas más importantes del sitio
- Haz fetch de `[dominio]/robots.txt` y `[dominio]/sitemap.xml`
- Analiza el HTML obtenido aplicando todas las dimensiones del reporte

**Sin URL** → analiza los archivos del proyecto actual en el sistema de archivos.

## Proceso de análisis

Ejecuta sequencialmente estos análisis (internamente, sin mostrar el proceso):
1. Meta tags y título de todas las páginas
2. Headings (H1-H6) y estructura de contenido
3. Imágenes y alt text
4. robots.txt y sitemap
5. Canonical tags
6. Structured data / JSON-LD
7. Performance signals (imágenes sin optimizar, lazy loading)
8. Internal linking básico
9. URLs y estructura

## Sistema de puntuación

Calcula una puntuación de 0-100 para cada dimensión:

| Dimensión | Peso |
|-----------|------|
| Meta tags (title + description) | 20% |
| Contenido y headings | 20% |
| Crawlability (robots, sitemap, canonical) | 15% |
| Imágenes | 15% |
| Schema / Structured data | 10% |
| Performance | 10% |
| Internal linking | 10% |

**Escala de puntuación total:**
- 85-100: Excelente 🟢
- 70-84: Bueno 🟡
- 50-69: Necesita mejoras 🟠
- 0-49: Crítico 🔴

## Formato del reporte

```markdown
# Reporte SEO — [Nombre del Proyecto]
**Fecha:** [fecha]
**URL del sitio:** [url]
**Preparado por:** SEO Toolkit

---

## Puntuación General: [X]/100 [emoji]

| Dimensión | Puntuación | Estado |
|-----------|-----------|--------|
| Meta Tags | X/20 | 🟢/🟡/🟠/🔴 |
| Contenido | X/20 | ... |
| Crawlability | X/15 | ... |
| Imágenes | X/15 | ... |
| Schema | X/10 | ... |
| Performance | X/10 | ... |
| Internal Linking | X/10 | ... |

---

## Resumen Ejecutivo

[2-3 párrafos describiendo el estado general del sitio, los problemas más importantes y el potencial de mejora con las optimizaciones recomendadas]

---

## Hallazgos por Dimensión

### 1. Meta Tags
**Puntuación: X/20**

[Tabla con estado de todas las páginas]

**Problemas encontrados:**
- 🔴 [crítico]: [descripción y páginas afectadas]
- 🟡 [importante]: [descripción]

---

### 2. Contenido y Headings
**Puntuación: X/20**
[Análisis y problemas]

---

### 3. Crawlability
**Puntuación: X/15**
[Análisis de robots.txt, sitemap, canonicals]

---

### 4. Imágenes
**Puntuación: X/15**
[Análisis de alt text, formatos, rendimiento]

---

### 5. Schema / Structured Data
**Puntuación: X/10**
[Análisis de JSON-LD existente y oportunidades]

---

### 6. Performance
**Puntuación: X/10**
[Señales de velocidad detectadas en el código]

---

### 7. Internal Linking
**Puntuación: X/10**
[Análisis de enlaces internos y páginas huérfanas]

---

## Plan de Acción Priorizado

### Semana 1 — Impacto inmediato (Quick wins)
1. ✅ [acción] → [archivo/página] → [impacto estimado]
2. ✅ [acción] → [archivo/página] → [impacto estimado]

### Semana 2-4 — Optimizaciones importantes
1. [acción] → [descripción detallada]

### Mes 2+ — Mejoras de largo plazo
1. [acción estratégica]

---

## Métricas a monitorear

Después de implementar las mejoras, monitorea:
- [ ] Impresiones en Google Search Console
- [ ] Posición promedio de keywords objetivo
- [ ] Core Web Vitals (LCP, CLS, INP)
- [ ] Tasa de click (CTR) en resultados de búsqueda
- [ ] Páginas indexadas vs. páginas del sitio

---

*Generado con SEO Toolkit — [fecha]*
```

Genera este reporte completo basándote en un análisis real de todos los archivos del proyecto.
