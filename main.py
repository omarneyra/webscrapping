import sys
import csv
import json
from deal_finder import (
    fetch_vtex_products,
    fetch_shopify_suggest_products,
    fetch_jumpseller_products,
    fetch_bsale_products,
    fetch_woocommerce_html_products,
    filter_and_rank_deals,
)
from analytics import (
    calculate_value_score,
    generate_verdict,
    build_optimal_basket,
    generate_market_insights,
)

# Palabras clave para rastreo de Whey y Caseína
SEARCH_QUERIES = [
    "whey",
    "caseina",
    "casein",
    "gold standard",
    "isolate",
    "iso 100",
    "rule 1",
    "mutant whey",
]


def export_to_csv(deals: list, filename: str = "cyber_deals.csv") -> None:
    """
    Exporta las ofertas ordenadas a un archivo CSV.
    """
    if not deals:
        return

    keys = [
        "source",
        "category",
        "title",
        "price",
        "original_price",
        "discount_pct",
        "weight_grams",
        "net_protein_grams",
        "cost_per_gram_clp",
        "value_score",
        "verdict_status",
        "verdict_reason",
        "permalink",
    ]

    flattened = []
    for d in deals:
        row = dict(d)
        verdict = d.get("verdict", {})
        row["verdict_status"] = verdict.get("status", "")
        row["verdict_reason"] = verdict.get("reason", "")
        flattened.append(row)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flattened)

    print(f"\n[+] Reporte CSV guardado en: {filename}")


def export_data_bundle(deals: list, insights: dict, baskets: dict, filename: str = "cyber_deals.json") -> None:
    """
    Exporta el bundle completo (deals + analítica + canasta) a JSON y JS para la web HTML5.
    """
    bundle = {
        "deals": deals,
        "insights": insights,
        "baskets": baskets,
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)
    print(f"[+] Bundle analítico JSON guardado en: {filename}")

    js_filename = filename.replace(".json", ".js")
    with open(js_filename, "w", encoding="utf-8") as f:
        f.write(f"window.CYBER_DATA = {json.dumps(bundle, indent=2, ensure_ascii=False)};\n")
        # Retrocompatibilidad
        f.write(f"window.CYBER_DEALS = {json.dumps(deals, indent=2, ensure_ascii=False)};\n")
    print(f"[+] Bundle JS sincronizado para la web en: {js_filename}")


def print_executive_summary(insights: dict, basket: dict) -> None:
    """
    Imprime en consola un resumen ejecutivo de inteligencia de mercado.
    """
    print("\n" + "=" * 90)
    print("               🧠 RESUMEN EJECUTIVO & INSIGHTS DE COMPRA")
    print("=" * 90)

    avg_costs = insights.get("avg_costs", {})
    print(f" • Promedio Whey en mercado:    ${avg_costs.get('whey', 0)} CLP por gramo de proteína")
    print(f" • Promedio Isolate en mercado: ${avg_costs.get('isolate', 0)} CLP por gramo de proteína")
    print(f" • Promedio Caseína en mercado: ${avg_costs.get('casein', 0)} CLP por gramo de proteína")
    print(f"\n • Veredicto Caseína:")
    print(f"   {insights.get('casein_tactical_advice', '')}")

    print("\n • Recomendación de Canasta Óptima (Abastecimiento 3 meses):")
    for it in basket.get("items", []):
        p = it["product"]
        print(f"   - {it['units']}x {p['title']} (${int(p['price']):,} c/u) -> {it['role']}")
    print(f"   Total canasta: ${int(basket.get('total_cost_clp', 0)):,} CLP (${basket.get('avg_cost_per_gram_clp', 0)}/g)")
    print(f"   Ahorro estimado vs mercado: ${int(basket.get('estimated_savings_clp', 0)):,} CLP")
    print("=" * 90)


def print_deals_table(deals: list, top_n: int = 25) -> None:
    """
    Imprime en consola las mejores ofertas formateadas con veredicto.
    """
    print("\n" + "=" * 135)
    print(f"{'#':<3} | {'SCORE':<5} | {'VEREDICTO':<18} | {'TIENDA':<14} | {'PRECIO':<10} | {'$/g PROT':<9} | {'PRODUCTO':<45} | {'ACCIÓN':<16}")
    print("=" * 135)

    for i, item in enumerate(deals[:top_n], start=1):
        score = f"{item.get('value_score', 0)}/100"
        verdict = item.get("verdict", {}).get("action", "Evaluar")[:18]
        source = item.get("source", "")[:14]
        price = f"${int(item.get('price', 0)):,}".replace(",", ".")
        cost_g = f"${item['cost_per_gram_clp']}" if item.get("cost_per_gram_clp") else "N/A"
        title = item.get("title", "")[:45]
        badge = item.get("verdict", {}).get("badge", "")[:16]

        print(f"{i:<3} | {score:<5} | {badge:<18} | {source:<14} | {price:<10} | {cost_g:<9} | {title:<45} | {verdict:<16}")

    print("=" * 135)


def enrich_products_with_analytics(products: list) -> list:
    """
    Calcula el Score de Valor y el Veredicto para cada producto.
    """
    enriched = []
    for p in products:
        item = dict(p)
        item["value_score"] = calculate_value_score(item)
        item["verdict"] = generate_verdict(item)
        enriched.append(item)
    return enriched


def run_tracker(
    target_category: str = "all",
    max_cost_per_gram: float = 65.0,
    min_discount: float = 0.0,
) -> None:
    """
    Ejecuta el rastreo de ofertas en vivo en tiendas especializadas de suplementos en Chile.
    """
    all_products = []

    print("[*] Consultando catálogo en Supletech (VTEX)...")
    supletech_items = fetch_vtex_products("Supletech", "https://supletech.cl", terms=["whey", "caseina", "proteina"])
    print(f"    -> {len(supletech_items)} variantes procesadas en Supletech.")
    all_products.extend(supletech_items)

    print("[*] Consultando catálogo en All Nutrition (Shopify)...")
    allnutrition_items = fetch_shopify_suggest_products("All Nutrition", "https://allnutrition.cl", queries=SEARCH_QUERIES)
    print(f"    -> {len(allnutrition_items)} productos procesados en All Nutrition.")
    all_products.extend(allnutrition_items)

    print("[*] Consultando catálogo en Winkler Nutrition (Shopify)...")
    winkler_items = fetch_shopify_suggest_products("Winkler Nutrition", "https://winklernutrition.cl", queries=SEARCH_QUERIES)
    print(f"    -> {len(winkler_items)} productos procesados en Winkler Nutrition.")
    all_products.extend(winkler_items)

    print("[*] Consultando catálogo en SportNutriShop (Shopify)...")
    sport_items = fetch_shopify_suggest_products("SportNutriShop", "https://www.sportnutrishop.cl", queries=SEARCH_QUERIES)
    print(f"    -> {len(sport_items)} productos procesados en SportNutriShop.")
    all_products.extend(sport_items)

    print("[*] Consultando catálogo en T4T (Shopify)...")
    t4t_items = fetch_shopify_suggest_products("T4T", "https://t4t.cl", queries=SEARCH_QUERIES)
    print(f"    -> {len(t4t_items)} productos procesados en T4T.")
    all_products.extend(t4t_items)

    print("[*] Consultando catálogo en MixGreen (Shopify)...")
    mix_items = fetch_shopify_suggest_products("MixGreen", "https://www.mixgreen.cl", queries=SEARCH_QUERIES)
    print(f"    -> {len(mix_items)} productos procesados en MixGreen.")
    all_products.extend(mix_items)

    print("[*] Consultando catálogo en GlobalNutrition (Shopify)...")
    global_items = fetch_shopify_suggest_products("GlobalNutrition", "https://globalnutrition.cl", queries=SEARCH_QUERIES)
    print(f"    -> {len(global_items)} productos procesados en GlobalNutrition.")
    all_products.extend(global_items)

    print("[*] Consultando catálogo en OutletFit (Jumpseller)...")
    outlet_items = fetch_jumpseller_products("OutletFit", "https://www.outletfit.cl", queries=["whey", "caseina", "proteina"])
    print(f"    -> {len(outlet_items)} productos procesados en OutletFit.")
    all_products.extend(outlet_items)

    print("[*] Consultando catálogo en Strongest (Bsale)...")
    strongest_items = fetch_bsale_products("Strongest", "https://www.strongest.cl", collection_paths=["/collection/proteinas"])
    print(f"    -> {len(strongest_items)} productos procesados en Strongest.")
    all_products.extend(strongest_items)

    print("[*] Consultando catálogo en ChileSuplementos (WooCommerce)...")
    cs_items = fetch_woocommerce_html_products(
        "ChileSuplementos",
        "https://www.chilesuplementos.cl",
        category_paths=[
            "/categoria/productos/tipo-de-proteina/whey-protein/",
            "/categoria/productos/tipo-de-proteina/caseina/",
            "/categoria/productos/tipo-de-proteina/whey-isolate/",
        ]
    )
    print(f"    -> {len(cs_items)} productos procesados en ChileSuplementos.")
    all_products.extend(cs_items)

    categories = None
    if target_category in ["whey", "casein", "isolate"]:
        categories = [target_category]

    ranked = filter_and_rank_deals(
        all_products,
        target_categories=categories,
        max_cost_per_gram=max_cost_per_gram if max_cost_per_gram > 0 else None,
        min_discount_pct=min_discount,
    )

    if not ranked:
        print("\n[-] No se encontraron ofertas que cumplan con los filtros.")
        return

    # Enriquecer con analítica y veredictos
    enriched_deals = enrich_products_with_analytics(ranked)
    # Ordenar por Score de Valor descendente (las mejores opciones primero)
    enriched_deals.sort(key=lambda x: (-x.get("value_score", 0), x.get("cost_per_gram_clp", 999)))

    # Generar inteligencia y canastas
    insights = generate_market_insights(enriched_deals)
    baskets = {
        "1_month": build_optimal_basket(enriched_deals, target_months=1),
        "3_months": build_optimal_basket(enriched_deals, target_months=3),
        "6_months": build_optimal_basket(enriched_deals, target_months=6),
    }

    print_executive_summary(insights, baskets["3_months"])
    print_deals_table(enriched_deals)

    export_to_csv(enriched_deals)
    export_data_bundle(enriched_deals, insights, baskets)


if __name__ == "__main__":
    cat = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    run_tracker(target_category=cat)
