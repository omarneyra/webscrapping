# ⚡ Cyber Protein Tracker Chile (CyberMonday Intelligence)

Sistema integral de web scraping, normalización multitienda, detección de ofertas reales y auditoría de calidad de laboratorio para suplementos deportivos (**Whey Protein, Whey Isolate y Caseína Micelar**) en el mercado chileno.

Diseñado bajo una **arquitectura por capas puramente procedural/funcional (sin POO/sin clases)** en Python, con soporte multiplataforma nativo (**Linux y Windows**), sistema de **caché condicional HTTP inteligente** (ETags y Content Hash) y **seguimiento histórico de precios**.

---

## 📑 Tabla de Contenidos
- [Objetivo y Métricas](#-objetivo-y-métricas)
- [Diseño y Arquitectura Técnica](#-diseño-y-arquitectura-técnica)
- [Matriz de Confianza de Marcas y Prevención de Spiking](#-matriz-de-confianza-de-marcas-y-prevención-de-spiking)
- [Tiendas y Plataformas Monitoreadas (12 Portales)](#-tiendas-y-plataformas-monitoreadas-12-portales)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Requisitos](#-instalación-y-requisitos)
- [Paso a Paso de Ejecución](#-paso-a-paso-de-ejecución)
  - [En Linux / macOS](#en-linux--macos)
  - [En Windows](#en-windows)
- [Detección de Cambios de Precio (Cyber vs Pre-Cyber)](#-detección-de-cambios-de-precio-cyber-vs-pre-cyber)
- [Ejecución de Pruebas Unitarias](#-ejecución-de-pruebas-unitarias)
- [Visualización del Dashboard Web](#-visualización-del-dashboard-web)

---

## 🎯 Objetivo y Métricas

A diferencia de los comparadores de precios convencionales que evalúan únicamente el precio bruto del envase, este sistema calcula el **costo por gramo de proteína biológicamente neta en CLP**:

$$\text{Costo por gramo neto (CLP/g)} = \frac{\text{Precio CLP}}{\text{Gramos de producto} \times \text{Ratio de Pureza}}$$

- **Ratios de pureza según suplemento:**
  - *Whey Isolate (WPI):* ~86% de proteína real.
  - *Whey Concentrado (WPC):* ~73% de proteína real.
  - *Caseína Micelar:* ~76% de proteína real.
- **Filtro antiruido:** Descarta automáticamente botellas, shakers, pre-entrenos, barras, snacks, líquidos (RTD) y muestras pequeñas (`< 350g`).
- **Value Score (0 a 100):** Algoritmo ponderado que evalúa:
  1. Eficiencia de costo por gramo (40%)
  2. Nivel de auditoría de marca / riesgo de amino spiking (25%)
  3. Descuento porcentual (15%)
  4. Formato y volumen del envase (12%)
  5. Tipo de proteína (8%)

---

## 🏗️ Diseño y Arquitectura Técnica

El proyecto está diseñado bajo el principio de **separación de responsabilidades en 5 capas desacopladas**, programadas con estilo funcional/procedural:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. CAPA DE CACHÉ (cache.py)                     │
│  - Descargas condicionales HTTP (If-None-Match / If-Modified-Since)    │
│  - Detección de HTTP 304 Not Modified (cero consumo de ancho de banda) │
│  - Hashing criptográfico SHA-256 para detectar cambios reales de DOM   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                     2. CAPA DE EXTRACCIÓN (extraction.py)              │
│  - Adaptadores específicos por plataforma de e-commerce:               │
│    • Shopify Suggest API       • VTEX Catalog Search API               │
│    • Jumpseller HTML parser    • Bsale HTML parser                     │
│    • WooCommerce Categories    • SuplementosAlMayor Cards (.shop-card) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    3. CAPA DE NORMALIZACIÓN (normalization.py)         │
│  - Estandarización de peso: lbs, kg, g (soporte para miles '2.350 g')  │
│  - Limpieza de precios chilenos ('$ 59.990 CLP' -> 59990.0)            │
│  - Estimación de gramos netos y costo por gramo en CLP                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                     4. CAPA DE ANÁLISIS (analytics.py)                 │
│  - Matriz de marcas y evidencia (Tier S, Tier A, Tier B, Tier C)       │
│  - Ponderación de Value Score (0 a 100) y veredictos de compra         │
│  - Tracking histórico de precios (price_history.json) Pre-Cyber        │
│  - Simulador de canasta óptima de abastecimiento (1, 3 y 6 meses)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                   5. CAPA DE PRESENTACIÓN (presentation.py)            │
│  - Exportación JSON UTF-8 (cyber_deals.json)                           │
│  - Exportación JS para navegador sin CORS (cyber_deals.js)             │
│  - Exportación CSV compatible con Excel UTF-8 BOM (cyber_deals.csv)    │
│  - Resumen ejecutivo en terminal y Dashboard HTML5 (index.html)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Matriz de Confianza de Marcas y Prevención de Spiking

Basado en el estudio de control de calidad proteica de **SERNAC / ODECU** y sellos internacionales de certificación:

| Nivel | Clasificación | Marcas Representativas | Sellos & Evidencia | Riesgo de Amino Spiking |
| :--- | :--- | :--- | :--- | :--- |
| **Tier S** | Estándar de Oro Mundial | Optimum Nutrition (ON), Dymatize, Ghost | *Informed-Choice*, *NSF for Sport*, cGMP USA, trazabilidad Glanbia QA. | **Nulo** |
| **Tier A** | Fabricantes Auditados | Mutant (Fit Foods), BioTechUSA, OstroVit, BSN, Rule 1, Animal | Regulación estricta *EFSA (Unión Europea)*, análisis lote a lote (J.S. Hamilton). | **Muy Bajo** |
| **Tier B** | Marcas Tradicionales | Winkler Nutrition, Ultimate Nutrition, Syntrax, BPI, Nutrex | Resolución Seremi Salud Chile, cGMP EE.UU. Materia prima láctea declarada. | **Bajo / Medio** |
| **Tier C** | Alerta / No Auditadas | Fit Protein, Briahlabs, Hexacore, 4Active, Shark Pro | Sin certificaciones de laboratorios independientes. Precios sospechosamente bajos ($22/g). | **Alto** (Relleno con aminoácidos libres o colágeno) |

---

## 🏪 Tiendas y Plataformas Monitoreadas (12 Portales)

El escáner cubre el espectro completo entre tiendas de retail deportivo y portales de venta al por mayor:

1. **All Nutrition** (`allnutrition.cl`) – Shopify API
2. **Supletech** (`supletech.cl`) – VTEX Catalog API
3. **Winkler Nutrition** (`winklernutrition.cl`) – Shopify API
4. **OutletFit** (`outletfit.cl`) – Jumpseller Scraper
5. **GlobalNutrition** (`globalnutrition.cl`) – Shopify API
6. **SportNutriShop** (`sportnutrishop.cl`) – Shopify API
7. **T4T Suplementos** (`t4t.cl`) – Shopify API
8. **MixGreen** (`mixgreen.cl`) – Shopify API
9. **Strongest** (`strongest.cl`) – Bsale Scraper (Catálogo regular y Packs x2/x3)
10. **ChileSuplementos** (`chilesuplementos.cl`) – WooCommerce Navigation Scraper
11. **SuplementosMayoristas** (`suplementosmayoristas.cl`) – VTEX Catalog API (Mayorista)
12. **SuplementosAlMayor** (`suplementosalmayor.cl`) – WooCommerce / B2BKing Scraper (Mayorista)

---

## 📁 Estructura del Proyecto

```text
cyber_protein_tracker/
├── app/
│   ├── __init__.py
│   ├── config.py          # Rutas con Pathlib (multiplataforma), catálogo de tiendas y benchmarks
│   ├── cache.py           # Descarga HTTP condicional (ETag, If-Modified-Since y SHA-256)
│   ├── normalization.py   # Parsing de pesos (lbs/kg/g), precios y pureza de proteína
│   ├── extraction.py      # Adaptadores para Shopify, VTEX, Jumpseller, Bsale y WooCommerce
│   ├── analytics.py       # Matriz de marcas, Value Score, historial de precios y canasta
│   ├── presentation.py    # Exportación a JSON, JS, CSV y formateadores de consola
│   └── main.py            # Orquestador del pipeline completo
├── tests/
│   ├── test_cache.py          # Pruebas unitarias de HTTP 304, SHA-256 y persistencia
│   ├── test_normalization.py  # Pruebas unitarias de parsing de peso, precios y pureza
│   └── test_analytics.py      # Pruebas de detección de marcas, scoring y canasta
├── data/
│   ├── http_cache.json        # Caché persistente de ETags y hashes de contenido
│   └── price_history.json     # Historial de precios Pre-Cyber por producto
├── main.py                # Punto de entrada raíz
├── run.sh                 # Lanzador ejecutable para Linux / macOS
├── run.bat                # Lanzador batch para Windows
├── index.html             # Dashboard interactivo HTML5 / CSS3 / Vanilla JS
├── cyber_deals.json       # Dataset analizado en JSON
├── cyber_deals.js         # Dataset exportado como variable global JS
├── cyber_deals.csv        # Dataset exportado en CSV para Excel
└── README.md              # Documentación técnica completa
```

---

## 🔧 Instalación y Requisitos

- **Python 3.9 o superior** (probado y compatible con Python 3.9 a 3.14).
- Dependencias estándar de Python:
  ```bash
  pip install requests beautifulsoup4
  ```

---

## 🚀 Paso a Paso de Ejecución

### En Linux / macOS
Puedes ejecutar el script bash que gestiona los permisos y el entorno:
```bash
# Dar permisos de ejecución si es la primera vez
chmod +x run.sh

# Ejecutar el pipeline
./run.sh
```
O directamente con Python:
```bash
python3 main.py
```

### En Windows
Haz doble clic en **`run.bat`** o ejecútalo desde el símbolo del sistema (`cmd` / `PowerShell`):
```cmd
run.bat
```
O directamente:
```cmd
python main.py
```

---

## 📈 Detección de Cambios de Precio (Cyber vs Pre-Cyber)

El sistema cuenta con una **línea base histórica registrada el 4 de Octubre de 2026** en `data/price_history.json`.

Cuando se ejecute el script tras la medianoche o durante el CyberMonday:
1. El motor comparará el precio publicado en vivo contra el precio base inicial (`initial_price`).
2. En el dashboard web aparecerá automáticamente una insignia:
   - `📉 Bajó $7.000 (-12.5%)`: Oferta real comprobada frente al precio pre-Cyber.
   - `📈 Subió $5.000 (+8.0%)`: Falsa oferta con precio inflado.
3. El filtro **`[📉 Rebajas Reales Cyber]`** en la barra superior aislará instantáneamente los productos con rebaja efectiva.

---

## 🧪 Ejecución de Pruebas Unitarias

El proyecto cuenta con **19 pruebas unitarias** que garantizan que el parsing, la caché condicional y el motor analítico funcionen sin regresiones:

```bash
# Ejecutar todas las pruebas unitarias
python3 -m unittest discover -s tests -v
```

Resultado esperado:
```text
Ran 19 tests in 0.006s
OK
```

---

## 💻 Visualización del Dashboard Web

El dashboard no requiere bases de datos externas ni servidores pesados. Puedes visualizarlo de dos formas:

1. **Servidor HTTP local (Recomendado):**
   ```bash
   python3 -m http.server 8000
   ```
   Abre en tu navegador: **`http://localhost:8000/index.html`**

2. **Doble clic directo:**
   Abre el archivo `index.html` con cualquier navegador moderno (Chrome, Firefox, Edge, Safari). Gracias a que los datos se exportan también en `cyber_deals.js`, el dashboard se cargará al instante sin bloqueos de seguridad por CORS local.
