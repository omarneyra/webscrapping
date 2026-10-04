import sys
import csv
from deal_finder import (
    fetch_vtex_products,
    fetch_shopify_suggest_products,
    filter_and_rank_deals,
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
        "permalink",
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(deals)

    print(f"\n[+] Reporte CSV guardado en: {filename}")


def export_to_json(deals: list, filename: str = "cyber_deals.json") -> None:
    """
    Exporta las ofertas ordenadas a formato JSON y JS para la web HTML5.
    """
    if not deals:
        return

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(deals, f, indent=2, ensure_ascii=False)
    print(f"[+] Reporte JSON guardado en: {filename}")

    # Archivo JS con asignación en window para abrir index.html directamente en el navegador sin problemas de CORS
    js_filename = filename.replace(".json", ".js")
    with open(js_filename, "w", encoding="utf-8") as f:
        f.write(f"window.CYBER_DEALS = {json.dumps(deals, indent=2, ensure_ascii=False)};\n")
    print(f"[+] Archivo JS guardado en: {js_filename}")


def print_deals_table(deals: list, top_n: int = 30) -> None:
    """
    Imprime en consola las mejores ofertas formateadas.
    """
    print("\n" + "=" * 125)
    print(f"{'#':<3} | {'TIENDA':<15} | {'TIPO':<8} | {'PRECIO':<11} | {'ANTES':<11} | {'DSCTO':<6} | {'$/g PROT':<9} | {'PRODUCTO':<50}")
    print("=" * 125)

    for i, item in enumerate(deals[:top_n], start=1):
        source = item.get("source", "")[:15]
        category = item.get("category", "")[:8].upper()
        price = f"${int(item.get('price', 0)):,}".replace(",", ".")
        orig = f"${int(item['original_price']):,}".replace(",", ".") if item.get("original_price") else "-"
        discount = f"{item.get('discount_pct', 0)}%" if item.get("discount_pct", 0) > 0 else "-"
        cost_g = f"${item['cost_per_gram_clp']}" if item.get("cost_per_gram_clp") else "N/A"
        title = item.get("title", "")[:50]

        print(f"{i:<3} | {source:<15} | {category:<8} | {price:<11} | {orig:<11} | {discount:<6} | {cost_g:<9} | {title:<50}")

    print("=" * 125)


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

    print(f"\n[+] Se encontraron {len(ranked)} ofertas ordenadas por costo/gramo de proteína neta:")
    print_deals_table(ranked)
    export_to_csv(ranked)
    export_to_json(ranked)


if __name__ == "__main__":
    cat = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    run_tracker(target_category=cat)
