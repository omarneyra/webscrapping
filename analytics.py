from typing import List, Dict, Any, Optional

# Benchmarks históricos del mercado chileno (CLP por gramo de proteína neta)
MARKET_BENCHMARKS = {
    "whey": {
        "exceptional": 35.0,  # Ganga real (< $35/g)
        "good": 45.0,         # Precio justo Cyber ($35 - $45/g)
        "regular": 55.0,      # Precio habitual de tienda ($45 - $55/g)
        "overpriced": 65.0,   # Sobreprecio (> $55/g)
    },
    "isolate": {
        "exceptional": 45.0,
        "good": 52.0,
        "regular": 60.0,
        "overpriced": 70.0,
    },
    "casein": {
        "exceptional": 48.0,
        "good": 58.0,
        "regular": 65.0,
        "overpriced": 75.0,
    },
}


def get_market_benchmark(category: str) -> Dict[str, float]:
    """
    Retorna los umbrales de referencia de precio/gramo según categoría.
    """
    return MARKET_BENCHMARKS.get(category, MARKET_BENCHMARKS["whey"])


def calculate_value_score(product: Dict[str, Any]) -> int:
    """
    Calcula una puntuación de valor de 0 a 100 para la compra.
    Pondera:
    - Eficiencia de costo por gramo (50%)
    - Descuento real (25%)
    - Formato y volumen del envase (15%)
    - Tipo y pureza de proteína (10%)
    """
    cost_g = product.get("cost_per_gram_clp")
    if not cost_g or cost_g <= 0:
        return 0

    cat = product.get("category", "whey")
    bench = get_market_benchmark(cat)

    # 1. Puntuación de costo (0 a 50 pts)
    if cost_g <= bench["exceptional"]:
        cost_score = 50.0
    elif cost_g <= bench["good"]:
        # interpolación entre exceptional y good
        factor = (bench["good"] - cost_g) / (bench["good"] - bench["exceptional"])
        cost_score = 35.0 + (factor * 15.0)
    elif cost_g <= bench["regular"]:
        factor = (bench["regular"] - cost_g) / (bench["regular"] - bench["good"])
        cost_score = 20.0 + (factor * 15.0)
    else:
        cost_score = max(5.0, 20.0 - ((cost_g - bench["regular"]) * 1.5))

    # 2. Puntuación de descuento (0 a 25 pts)
    discount = float(product.get("discount_pct", 0.0))
    if discount >= 35.0:
        disc_score = 25.0
    elif discount >= 20.0:
        disc_score = 18.0 + ((discount - 20.0) / 15.0) * 7.0
    elif discount >= 10.0:
        disc_score = 10.0 + ((discount - 10.0) / 10.0) * 8.0
    else:
        disc_score = max(0.0, discount)

    # 3. Puntuación por tamaño/formato (0 a 15 pts) - Envases grandes rinden más
    weight_g = float(product.get("weight_grams") or 0.0)
    if weight_g >= 4000:       # 10 lbs o saco
        size_score = 15.0
    elif weight_g >= 2000:     # 5 lbs o 2-2.5 kg
        size_score = 12.0
    elif weight_g >= 900:      # 2 lbs / 1 kg
        size_score = 7.0
    else:
        size_score = 3.0

    # 4. Tipo de suplemento (0 a 10 pts)
    type_bonus = 10.0 if cat in ["isolate", "casein"] else 8.0

    total = int(round(cost_score + disc_score + size_score + type_bonus))
    return max(5, min(100, total))


def generate_verdict(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Emite un veredicto estructurado de compra: si conviene comprar o abstenerse.
    """
    cost_g = product.get("cost_per_gram_clp")
    disc = float(product.get("discount_pct", 0.0))
    cat = product.get("category", "whey")
    bench = get_market_benchmark(cat)
    score = calculate_value_score(product)

    if not cost_g:
        return {
            "status": "SIN_DATOS",
            "badge": "⚠️ Sin peso claro",
            "badge_color": "gray",
            "action": "Verificar ficha",
            "reason": "No fue posible determinar el peso neto en polvo de forma confiable.",
            "value_score": score,
        }

    # Criterio 1: Ganga absoluta de Cyber
    if cost_g <= bench["exceptional"] or (score >= 82 and disc >= 15):
        return {
            "status": "COMPRA_INMEDIATA",
            "badge": "🔥 Ganga Real / Compra Maestra",
            "badge_color": "emerald",
            "action": "Comprar ahora",
            "reason": f"Excelente ratio de ${cost_g} CLP/g. Precio por debajo del piso histórico del mercado.",
            "value_score": score,
        }

    # Criterio 2: Buena alternativa sólida
    if cost_g <= bench["good"] or score >= 65:
        return {
            "status": "BUENA_OPCION",
            "badge": "✅ Compra Conveniente",
            "badge_color": "cyan",
            "action": "Recomendado",
            "reason": f"Precio justo Cyber (${cost_g} CLP/g). Cumple estándar de calidad y formato rentable.",
            "value_score": score,
        }

    # Criterio 3: Falsa oferta / Inflado
    if disc >= 20.0 and cost_g > bench["regular"]:
        return {
            "status": "INFLADO",
            "badge": "❌ Falsa Oferta (Precio Inflado)",
            "badge_color": "rose",
            "action": "No comprar",
            "reason": f"Tiene un supuesto descuento del {disc}%, pero su costo por gramo (${cost_g}) sigue siendo elevado.",
            "value_score": score,
        }

    # Criterio 4: Caro / No conveniente
    if cost_g > bench["good"]:
        return {
            "status": "NO_CONVIENE",
            "badge": "⚠️ Caro / Esperar Rebaja",
            "badge_color": "amber",
            "action": "Esperar",
            "reason": f"Costo por gramo (${cost_g} CLP/g) superior a la media de conveniencia. Conviene buscar formato mayor.",
            "value_score": score,
        }

    return {
        "status": "REGULAR",
        "badge": "ℹ️ Opción Regular",
        "badge_color": "blue",
        "action": "Evaluar según stock",
        "reason": f"Precio de mercado estándar sin descuento llamativo.",
        "value_score": score,
    }


def build_optimal_basket(products: List[Dict[str, Any]], target_months: int = 3) -> Dict[str, Any]:
    """
    Calcula la canasta óptima de abastecimiento para N meses.
    Asume:
    - 1 scoop diario de Whey (aprox. 25g de proteína neta / día = 750g/mes)
    - 1 scoop nocturno de Caseína en días de entrenamiento (~15-20 días/mes = 400g/mes)
    """
    whey_candidates = [p for p in products if p.get("category") == "whey" and p.get("cost_per_gram_clp")]
    casein_candidates = [p for p in products if p.get("category") == "casein" and p.get("cost_per_gram_clp")]

    whey_candidates.sort(key=lambda x: (x.get("cost_per_gram_clp", 999), -x.get("discount_pct", 0)))
    casein_candidates.sort(key=lambda x: (x.get("cost_per_gram_clp", 999), -x.get("discount_pct", 0)))

    selected_whey = whey_candidates[0] if whey_candidates else None
    selected_casein = casein_candidates[0] if casein_candidates else None

    # Si para abastecer N meses se requieren múltiples potes de Whey
    needed_whey_prot = 750.0 * target_months
    needed_casein_prot = 400.0 * target_months

    whey_units = 1
    if selected_whey and selected_whey.get("net_protein_grams"):
        whey_units = max(1, int(round(needed_whey_prot / selected_whey["net_protein_grams"])))

    casein_units = 1
    if selected_casein and selected_casein.get("net_protein_grams"):
        casein_units = max(1, int(round(needed_casein_prot / selected_casein["net_protein_grams"])))

    total_cost = 0.0
    total_protein = 0.0
    items = []

    if selected_whey:
        cost = selected_whey["price"] * whey_units
        prot = (selected_whey.get("net_protein_grams") or 0.0) * whey_units
        total_cost += cost
        total_protein += prot
        items.append({
            "product": selected_whey,
            "units": whey_units,
            "role": "Proteína Base Diaria (Whey)",
            "subtotal": cost,
        })

    if selected_casein:
        cost = selected_casein["price"] * casein_units
        prot = (selected_casein.get("net_protein_grams") or 0.0) * casein_units
        total_cost += cost
        total_protein += prot
        items.append({
            "product": selected_casein,
            "units": casein_units,
            "role": "Recuperación Nocturna (Caseína)",
            "subtotal": cost,
        })

    avg_cost_per_gram = round(total_cost / total_protein, 2) if total_protein > 0 else 0.0

    # Estimación de ahorro respecto a comprar marcas infladas a precio regular ($58 CLP/g de mercado)
    reference_market_cost = total_protein * 58.0
    estimated_savings = max(0.0, reference_market_cost - total_cost)

    return {
        "target_months": target_months,
        "items": items,
        "total_cost_clp": total_cost,
        "total_protein_grams": total_protein,
        "avg_cost_per_gram_clp": avg_cost_per_gram,
        "estimated_savings_clp": estimated_savings,
        "daily_cost_clp": round(total_cost / (target_months * 30), 0) if target_months > 0 else 0,
    }


def generate_market_insights(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Genera el diagnóstico estratégico global del mercado de suplementos para este Cyber.
    """
    valid = [p for p in products if p.get("cost_per_gram_clp")]
    if not valid:
        return {"error": "Sin productos válidos"}

    whey_items = [p for p in valid if p.get("category") == "whey"]
    casein_items = [p for p in valid if p.get("category") == "casein"]
    isolate_items = [p for p in valid if p.get("category") == "isolate"]

    avg_whey_cost = round(sum(p["cost_per_gram_clp"] for p in whey_items) / len(whey_items), 2) if whey_items else 0
    avg_casein_cost = round(sum(p["cost_per_gram_clp"] for p in casein_items) / len(casein_items), 2) if casein_items else 0
    avg_iso_cost = round(sum(p["cost_per_gram_clp"] for p in isolate_items) / len(isolate_items), 2) if isolate_items else 0

    best_whey = min(whey_items, key=lambda x: x["cost_per_gram_clp"]) if whey_items else None
    best_casein = min(casein_items, key=lambda x: x["cost_per_gram_clp"]) if casein_items else None

    # Evaluación de la prima por Caseína:
    # Si la caseína está más de un 35% más cara que la Whey, la recomendación técnica es no sobreabastecerse de caseína.
    casein_premium_pct = 0.0
    if avg_whey_cost > 0 and avg_casein_cost > 0:
        casein_premium_pct = round(((avg_casein_cost - avg_whey_cost) / avg_whey_cost) * 100.0, 1)

    casein_tactical_advice = (
        f"La caseína tiene una prima de sobreprecio de {casein_premium_pct}% respecto a la Whey. "
        "Recomendación: Compra solo 1 envase de caseína para rotación nocturna y concentra el 75%+ de tu presupuesto en Whey de 5 Lb."
        if casein_premium_pct > 25.0 else
        "La caseína presenta precios competitivos cercanos a la Whey. Excelente momento para abastecerse de ambas."
    )

    # Tiendas más competitivas
    stores_summary = {}
    for p in valid:
        s = p.get("source", "Otro")
        if s not in stores_summary:
            stores_summary[s] = []
        stores_summary[s].append(p["cost_per_gram_clp"])

    store_rankings = []
    for s, costs in stores_summary.items():
        store_rankings.append({
            "store": s,
            "avg_cost_clp": round(sum(costs) / len(costs), 2),
            "min_cost_clp": min(costs),
            "offer_count": len(costs),
        })
    store_rankings.sort(key=lambda x: x["min_cost_clp"])

    return {
        "avg_costs": {
            "whey": avg_whey_cost,
            "casein": avg_casein_cost,
            "isolate": avg_iso_cost,
        },
        "best_picks": {
            "whey": best_whey,
            "casein": best_casein,
        },
        "casein_premium_pct": casein_premium_pct,
        "casein_tactical_advice": casein_tactical_advice,
        "store_rankings": store_rankings,
    }
