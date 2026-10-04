import time
from typing import Dict, Any

from app.config import (
    STORES_CATALOG,
    SEARCH_QUERIES,
    CACHE_FILE,
    DEALS_JSON,
    DEALS_JS,
    DEALS_CSV,
)
from app.cache import load_cache, save_cache
from app.extraction import scrape_all_stores
from app.analytics import (
    enrich_products_with_analytics,
    build_optimal_basket,
    generate_market_insights,
)
from app.presentation import (
    export_deals_json,
    export_deals_js,
    export_deals_csv,
    print_summary_terminal,
)


def run_pipeline() -> Dict[str, Any]:
    """
    Función principal que orquesta la ejecución completa por capas:
    1. Capa de Caché: Carga el almacenamiento de respuestas previas (ETag / SHA-256).
    2. Capa de Extracción: Descarga y parsea solo lo que cambió de las tiendas chilenas.
    3. Capa de Normalización: Estandariza pesos, precios y calcula pureza neta.
    4. Capa de Análisis: Evalúa marcas (Tier S/A/B/C), calcula Value Score y canasta óptima.
    5. Capa de Presentación: Exporta JSON, JS, CSV y muestra resumen en consola.
    """
    print("Iniciando escaneo inteligente de suplementos...")

    # 1. Cargar caché existente
    cache_store = load_cache(CACHE_FILE)
    initial_cached_urls = len(cache_store)
    print(f"[Caché] Entradas registradas previamente: {initial_cached_urls}")

    # 2. Extracción y Normalización
    raw_products = scrape_all_stores(STORES_CATALOG, SEARCH_QUERIES, cache_store)
    print(f"[Extracción] Total productos capturados: {len(raw_products)}")

    # Guardar estado de caché actualizado
    save_cache(cache_store, CACHE_FILE)

    # 3. Análisis Inteligente
    enriched_products = enrich_products_with_analytics(raw_products)
    market_insights = generate_market_insights(enriched_products)
    optimal_basket = build_optimal_basket(enriched_products, target_months=3)

    payload: Dict[str, Any] = {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_stores_scanned": len(STORES_CATALOG),
            "total_products_scanned": len(raw_products),
            "analyzed_deals_count": len(enriched_products),
        },
        "insights": market_insights,
        "optimal_basket": optimal_basket,
        "deals": enriched_products,
    }

    # 4. Presentación y Exportación
    export_deals_json(payload, DEALS_JSON)
    export_deals_js(payload, DEALS_JS)
    export_deals_csv(enriched_products, DEALS_CSV)
    print_summary_terminal(payload)

    return payload


if __name__ == "__main__":
    run_pipeline()
