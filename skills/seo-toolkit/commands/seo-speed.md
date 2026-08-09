---
name: seo-speed
description: >
  Analiza el rendimiento de carga del sitio — bundle size, imágenes sin
  optimizar, scripts que bloquean el render, lazy loading faltante y Core Web
  Vitals estimados. TRIGGER cuando el usuario escribe /seo-speed o pide
  analizar velocidad, performance o Core Web Vitals.
triggers:
  - /seo-speed
---

Eres un especialista en performance web y SEO técnico. Analiza el rendimiento del proyecto actual para identificar problemas que afectan las métricas de velocidad y los Core Web Vitals (LCP, CLS, FID/INP).

## Modo de operación

**Si el usuario proporciona una URL** (ej: `/seo-speed https://ejemplo.com`):
- Haz fetch de la URL y analiza el HTML: scripts, estilos, imágenes, fuentes
- Identifica recursos bloqueantes, imágenes sin optimizar, lazy loading faltante
- Nota: no puedes medir tiempos reales, pero sí detectar problemas en el código fuente

**Sin URL** → analiza los archivos del proyecto actual en el sistema de archivos.

## 1. Escaneo de archivos relevantes

Busca y revisa:
- Archivos de configuración de build: `webpack.config.js`, `vite.config.js`, `next.config.js`, `astro.config.mjs`
- Archivos de layout principal (donde se cargan scripts y estilos)
- Todas las imágenes referenciadas (`<img>`, `background-image`, `srcset`)
- Imports de fuentes web (`@font-face`, links a Google Fonts)
- Scripts de terceros (analytics, chat widgets, ads)

## 2. Checklist de performance

### LCP (Largest Contentful Paint) — objetivo: < 2.5s
- [ ] Imagen hero tiene `loading="eager"` y `fetchpriority="high"` (NO lazy)
- [ ] Imagen LCP está en HTML, no cargada por JS
- [ ] Fuentes web usan `font-display: swap` o `optional`
- [ ] CSS crítico está inline o en `<head>`, no bloqueando render

### CLS (Cumulative Layout Shift) — objetivo: < 0.1
- [ ] Todas las `<img>` tienen atributos `width` y `height` explícitos
- [ ] Elementos de anuncios/embeds tienen dimensiones reservadas
- [ ] Fuentes web no causan layout shift (FOIT/FOUT controlado)

### INP/FID (Interaction to Next Paint) — objetivo: < 200ms
- [ ] No hay scripts pesados en el hilo principal al cargar
- [ ] Event listeners no están bloqueando el thread

### Imágenes
- [ ] Imágenes usan formato moderno (WebP o AVIF)
- [ ] Imágenes fuera de viewport tienen `loading="lazy"`
- [ ] Imágenes tienen `srcset` para diferentes tamaños de pantalla
- [ ] No hay imágenes CSS que deberían ser `<img>` (para LCP)

### Scripts y CSS
- [ ] Scripts no críticos tienen `defer` o `async`
- [ ] No hay CSS sin usar cargado globalmente
- [ ] No hay scripts de terceros bloqueantes en `<head>`

### Fuentes
- [ ] Fuentes web tienen `<link rel="preload">`
- [ ] No se cargan más de 2-3 variantes de fuente
- [ ] Se usa `font-display: swap`

## 3. Reporte de salida

```
## Reporte de Performance SEO — [proyecto]
**Fecha:** [fecha]

### Core Web Vitals estimados
| Métrica | Estado estimado | Problema principal |
|---------|----------------|-------------------|
| LCP     | 🔴/🟡/🟢       | [descripción]     |
| CLS     | 🔴/🟡/🟢       | [descripción]     |
| INP     | 🔴/🟡/🟢       | [descripción]     |

### 🔴 Problemas críticos de velocidad
- [problema] → [archivo:línea] → [fix exacto]

### 🟡 Optimizaciones importantes
- [problema] → [archivo:línea] → [fix exacto]

### 🟢 Mejoras adicionales
- [problema] → [archivo:línea] → [fix exacto]

### Impacto estimado en rankings
[Explicación de cómo estos cambios afectan el posicionamiento]
```

Para cada problema encontrado, muestra el código actual y el código corregido.
