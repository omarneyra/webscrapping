import json
import csv
from pathlib import Path
from typing import List, Dict, Any


def export_deals_json(data: Dict[str, Any], filepath: Path) -> None:
    """
    Exporta el dataset completo analizado en formato JSON UTF-8.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_deals_js(data: Dict[str, Any], filepath: Path) -> None:
    """
    Exporta el dataset como variable JavaScript para consumo directo en el navegador web
    sin requerir servidores web complejos ni problemas de CORS en filesystem local.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"window.CYBER_DEALS_DATA = {json.dumps(data, indent=2, ensure_ascii=False)};\n")


def export_deals_csv(products: List[Dict[str, Any]], filepath: Path) -> None:
    """
    Exporta el ranking de productos en CSV compatible con Excel (UTF-8 con BOM o delimitador estándar).
    """
    if not products:
        return

    filepath.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "source",
        "title",
        "category",
        "price",
        "original_price",
        "discount_pct",
        "weight_grams",
        "net_protein_grams",
        "cost_per_gram_clp",
        "value_score",
        "brand_tier",
        "brand_name",
        "verdict_status",
        "permalink",
    ]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in products:
            writer.writerow({
                "source": item.get("source", ""),
                "title": item.get("title", ""),
                "category": item.get("category", ""),
                "price": item.get("price", 0),
                "original_price": item.get("original_price") or "",
                "discount_pct": item.get("discount_pct", 0),
                "weight_grams": item.get("weight_grams") or "",
                "net_protein_grams": item.get("net_protein_grams") or "",
                "cost_per_gram_clp": item.get("cost_per_gram_clp") or "",
                "value_score": item.get("value_score", 0),
                "brand_tier": item.get("brand_trust", {}).get("tier", ""),
                "brand_name": item.get("brand_trust", {}).get("brand_name", ""),
                "verdict_status": item.get("verdict", {}).get("status", ""),
                "permalink": item.get("permalink", ""),
            })


def print_summary_terminal(data: Dict[str, Any]) -> None:
    """
    Imprime en consola un resumen ejecutivo del escaneo.
    """
    meta = data.get("meta", {})
    insights = data.get("insights", {})
    basket = data.get("optimal_basket", {})

    print("\n" + "=" * 65)
    print(" 🚀 RESUMEN INTELIGENTE - CYBERMONDAY SUPLEMENTOS CHILE")
    print("=" * 65)
    print(f"Tiendas analizadas: {meta.get('total_stores_scanned', 0)}")
    print(f"Productos analizados: {meta.get('total_products_scanned', 0)}")
    print(f"Productos con métricas: {meta.get('analyzed_deals_count', 0)}")

    if "avg_costs" in insights:
        print("\n[📊 Costo Promedio por Gramo de Proteína]")
        print(f"  • Whey Concentrado:  ${insights['avg_costs'].get('whey', 0)} CLP/g")
        print(f"  • Whey Isolate:      ${insights['avg_costs'].get('isolate', 0)} CLP/g")
        print(f"  • Caseína Micelar:   ${insights['avg_costs'].get('casein', 0)} CLP/g")

    if basket and "items" in basket:
        print(f"\n[🛒 Canasta Óptima Sugerida ({basket.get('target_months', 3)} Meses)]")
        for item in basket["items"]:
            prod = item["product"]
            print(f"  • {item['role']}: {item['units']}x {prod['title']} (${prod['price']:,} CLP c/u)")
        print(f"  -> Total Estimado:   ${basket.get('total_cost_clp', 0):,.0f} CLP")
        print(f"  -> Ahorro Estimado:  ${basket.get('estimated_savings_clp', 0):,.0f} CLP")

    print("=" * 65 + "\n")
