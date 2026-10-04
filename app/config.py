from pathlib import Path

# Rutas multiplataforma (compatibles con Linux y Windows)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_FILE = DATA_DIR / "http_cache.json"
DEALS_JSON = BASE_DIR / "cyber_deals.json"
DEALS_JS = BASE_DIR / "cyber_deals.js"
DEALS_CSV = BASE_DIR / "cyber_deals.csv"

# Asegurar existencia de directorio de datos
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Consultas de búsqueda estándar
SEARCH_QUERIES = [
    "whey",
    "caseina",
    "casein",
    "gold standard",
    "isolate",
    "iso 100",
    "mutant whey",
]

# Directorio de tiendas chilenas y sus adaptadores
STORES_CATALOG = [
    {
        "name": "All Nutrition",
        "type": "shopify",
        "url": "https://allnutrition.cl",
    },
    {
        "name": "Supletech",
        "type": "vtex",
        "url": "https://supletech.cl",
        "terms": ["whey", "caseina", "proteina"],
    },
    {
        "name": "Winkler Nutrition",
        "type": "shopify",
        "url": "https://winklernutrition.cl",
    },
    {
        "name": "SportNutriShop",
        "type": "shopify",
        "url": "https://www.sportnutrishop.cl",
    },
    {
        "name": "T4T",
        "type": "shopify",
        "url": "https://t4t.cl",
    },
    {
        "name": "MixGreen",
        "type": "shopify",
        "url": "https://www.mixgreen.cl",
    },
    {
        "name": "GlobalNutrition",
        "type": "shopify",
        "url": "https://globalnutrition.cl",
    },
    {
        "name": "OutletFit",
        "type": "jumpseller",
        "url": "https://www.outletfit.cl",
        "queries": ["whey", "caseina", "proteina"],
    },
    {
        "name": "Strongest",
        "type": "bsale",
        "url": "https://www.strongest.cl",
        "paths": ["/collection/proteinas", "/collection/pack-s-x2"],
    },
    {
        "name": "ChileSuplementos",
        "type": "woocommerce",
        "url": "https://www.chilesuplementos.cl",
        "paths": [
            "/categoria/productos/tipo-de-proteina/whey-protein/",
            "/categoria/productos/tipo-de-proteina/caseina/",
            "/categoria/productos/tipo-de-proteina/whey-isolate/",
        ],
    },
    {
        "name": "SuplementosMayoristas",
        "type": "vtex",
        "url": "https://www.suplementosmayoristas.cl",
        "terms": ["whey", "proteina"],
    },
    {
        "name": "SuplementosAlMayor",
        "type": "suplementosalmayor",
        "url": "https://suplementosalmayor.cl",
        "paths": [
            "/product-category/productos/tipo-de-proteina/whey-protein/",
            "/product-category/productos/tipo-de-proteina/caseina/",
            "/product-category/productos/tipo-de-proteina/whey-isolate/",
        ],
    },
]

# Conversión y ratios de pureza
LBS_TO_GRAMS = 453.592
KG_TO_GRAMS = 1000.0

PROTEIN_PURITY_RATIOS = {
    "isolate": 0.86,
    "whey": 0.73,
    "casein": 0.76,
    "default": 0.73,
}

MARKET_BENCHMARKS = {
    "whey": {"exceptional": 35.0, "good": 45.0, "regular": 55.0, "overpriced": 65.0},
    "isolate": {"exceptional": 45.0, "good": 52.0, "regular": 60.0, "overpriced": 70.0},
    "casein": {"exceptional": 48.0, "good": 58.0, "regular": 65.0, "overpriced": 75.0},
}
