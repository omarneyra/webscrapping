# CyberMonday Chile - Tracker de Proteínas (Whey & Caseína)

Herramienta de web scraping y análisis en tiempo real para rastrear y detectar ofertas verdaderas de suplementos deportivos (Whey Protein, Caseína Micelar e Isolate) en el CyberMonday de Chile.

## 🎯 Objetivo y Métricas

A diferencia de monitores tradicionales que solo comparan precios brutos, este rastreador calcula el **costo por gramo de proteína real en CLP**:

$$\text{Costo por gramo} = \frac{\text{Precio CLP}}{\text{Gramos de producto} \times \text{Pureza}}$$

- **Pureza estimada:** Whey (~73%), Isolate (~86%), Caseína (~76%).
- **Detección de trampas:** Descarta shakers, barras, bebidas líquidas (RTD) y suplementos con rellenos.

## 🛒 Tiendas Monitoreadas

- **All Nutrition** (Shopify API)
- **Supletech** (VTEX Catalog API)
- **Winkler Nutrition** (Shopify API)

## 📁 Estructura del Proyecto

- `deal_finder.py`: Lógica procedimental de parsing, normalización de pesos (lbs, kg, g) y ranking de ofertas.
- `main.py`: Script ejecutable para consultar APIs y exportar a CSV, JSON y JS.
- `index.html`: Dashboard web interactivo HTML5 con filtros en vivo, búsqueda por marca/formato y tarjetas responsivas.
- `test_deal_finder.py`: Batería de pruebas unitarias (`unittest`).
- `cyber_deals.json` / `cyber_deals.csv`: Datos recopilados en tiempo real.

## 🚀 Uso Rápido

### 1. Ejecutar el rastreador en Python
```bash
# Rastrear todo (Whey, Caseína e Isolate)
python main.py

# Rastrear solo Caseína
python main.py casein

# Rastrear solo Whey
python main.py whey
```

### 2. Ejecutar las pruebas unitarias
```bash
python -m unittest -v test_deal_finder.py
```

### 3. Visualizar en la Web
Abre directamente `index.html` en tu navegador o inicia un servidor simple:
```bash
python -m http.server 8000
```
Y accede a `http://localhost:8000`.
