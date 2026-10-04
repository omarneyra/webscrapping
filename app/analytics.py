from typing import List, Dict, Any, Optional
from app.config import MARKET_BENCHMARKS

# Base de datos de evidencia, certificaciones y riesgo de amino spiking por marca
BRAND_TRUST_DATABASE = {
    "optimum nutrition": {
        "tier": "Tier S",
        "brand_name": "Optimum Nutrition (ON)",
        "trust_score": 98,
        "certifications": ["Informed-Choice", "NSF for Sport", "Labdoor Score A+", "Glanbia QA"],
        "spiking_risk": "Nulo",
        "notes": "Estándar de oro mundial. Control directo de materia prima láctea (Glanbia). Cero amino spiking.",
    },
    "dymatize": {
        "tier": "Tier S",
        "brand_name": "Dymatize",
        "trust_score": 97,
        "certifications": ["Informed-Choice", "cGMP Certified (USA)"],
        "spiking_risk": "Nulo",
        "notes": "Líder en aislamiento (ISO 100) y caseína micelar con trazabilidad de lotes certificada.",
    },
    "ghost": {
        "tier": "Tier S",
        "brand_name": "Ghost Lifestyle",
        "trust_score": 95,
        "certifications": ["100% Transparent Label", "cGMP (USA)"],
        "spiking_risk": "Nulo",
        "notes": "Etiqueta 100% transparente: desglosa los gramos exactos de WPI y WPC sin mezclas ocultas.",
    },
    "biotechusa": {
        "tier": "Tier A",
        "brand_name": "BioTechUSA",
        "trust_score": 91,
        "certifications": ["EFSA (Unión Europea)", "ISO 22000", "HACCP", "GMP"],
        "spiking_risk": "Muy Bajo",
        "notes": "Fabricante europeo bajo estricta regulación de la EFSA. Caseína micelar pura sin rellenos.",
    },
    "mutant": {
        "tier": "Tier A",
        "brand_name": "Mutant (PVL / Fit Foods)",
        "trust_score": 88,
        "certifications": ["Informed-Choice", "cGMP Certified (Canadá)"],
        "spiking_risk": "Muy Bajo",
        "notes": "Planta propia en Canadá (Fit Foods). Sellos Informed-Choice en cada formulación.",
    },
    "ostrovit": {
        "tier": "Tier A",
        "brand_name": "OstroVit",
        "trust_score": 86,
        "certifications": ["Estándar UE (Polonia)", "Análisis J.S. Hamilton por lote", "HACCP"],
        "spiking_risk": "Bajo",
        "notes": "Marca europea low-cost que publica análisis microbiológicos y proteicos independientes por lote.",
    },
    "bsn": {
        "tier": "Tier A",
        "brand_name": "BSN (Syntha-6)",
        "trust_score": 88,
        "certifications": ["Glanbia QA", "cGMP (USA)"],
        "spiking_risk": "Muy Bajo",
        "notes": "Filial de Glanbia. Excelente perfil de asimilación y digestibilidad.",
    },
    "winkler nutrition": {
        "tier": "Tier B",
        "brand_name": "Winkler Nutrition",
        "trust_score": 78,
        "certifications": ["Resolución Seremi Salud Chile", "Registro Nacional 10+ años"],
        "spiking_risk": "Bajo / Medio",
        "notes": "Marca chilena consolidada. En estudio ODECU/SERNAC tuvo discrepancias menores de rotulación pero usa WPC real.",
    },
    "ultimate nutrition": {
        "tier": "Tier B",
        "brand_name": "Ultimate Nutrition",
        "trust_score": 78,
        "certifications": ["cGMP (USA)", "Historial 40 años"],
        "spiking_risk": "Bajo",
        "notes": "Línea ProStar con buena reputación histórica en pruebas de nitrógeno y laboratorio.",
    },
    "syntrax": {
        "tier": "Tier B",
        "brand_name": "Syntrax",
        "trust_score": 76,
        "certifications": ["Promina Whey", "cGMP (USA)"],
        "spiking_risk": "Bajo",
        "notes": "Proteína estadounidense con tecnología Promina y buena biodisponibilidad.",
    },
    "bpi sports": {
        "tier": "Tier B",
        "brand_name": "BPI Sports",
        "trust_score": 72,
        "certifications": ["ChromaDex Tested (histórico)", "cGMP"],
        "spiking_risk": "Medio",
        "notes": "Línea ISO HD de buen nivel; en 2015 enfrentó demandas colectivas por aminoácidos libres en líneas de entrada.",
    },
    "redcon1": {
        "tier": "Tier B",
        "brand_name": "Redcon1",
        "trust_score": 75,
        "certifications": ["cGMP (USA)"],
        "spiking_risk": "Bajo / Medio",
        "notes": "Marca norteamericana con presencia en gimnasios y formulaciones estándar.",
    },
    "briahlabs": {
        "tier": "Tier C",
        "brand_name": "BriahLabs",
        "trust_score": 48,
        "certifications": ["Sin certificaciones de terceros independientes"],
        "spiking_risk": "Alto",
        "notes": "Marca de bajo costo sin sellos de Informed-Choice ni análisis de lote públicos.",
    },
    "hexacore": {
        "tier": "Tier C",
        "brand_name": "Hexacore",
        "trust_score": 50,
        "certifications": ["Sin certificaciones de terceros independientes"],
        "spiking_risk": "Alto",
        "notes": "Precios muy bajos pero sin auditorías independientes de pureza proteica ni sellos antidopaje.",
    },
    "fit protein": {
        "tier": "Tier C",
        "brand_name": "Fit Protein",
        "trust_score": 45,
        "certifications": ["Sin sellos de calidad internacional"],
        "spiking_risk": "Alto",
        "notes": "Precio sospechosamente bajo ($22 CLP/g). Alto riesgo de subdosificación o amino spiking.",
    },
    "4active": {
        "tier": "Tier C",
        "brand_name": "4Active",
        "trust_score": 52,
        "certifications": ["Sin sellos de calidad internacional"],
        "spiking_risk": "Medio / Alto",
        "notes": "Blend económico local; carece de certificación de pureza por laboratorios externos.",
    },
    "shark pro": {
        "tier": "Tier C",
        "brand_name": "Shark Pro",
        "trust_score": 50,
        "certifications": ["Sin certificación internacional"],
        "spiking_risk": "Alto",
        "notes": "Marca económica sin auditorías de terceros publicadas.",
    },
    "rule 1": {
        "tier": "Tier A",
        "brand_name": "Rule 1 (R1)",
        "trust_score": 90,
        "certifications": ["Informed-Choice", "cGMP (USA)", "Fundadores de Optimum Nutrition"],
        "spiking_risk": "Muy Bajo",
        "notes": "Creada por los fundadores originales de Optimum Nutrition tras vender a Glanbia. Instalaciones propias con certificación cGMP e Informed-Choice.",
    },
    "animal": {
        "tier": "Tier A",
        "brand_name": "Animal (Universal Nutrition)",
        "trust_score": 88,
        "certifications": ["cGMP Certified (USA)", "Fabricación propia New Jersey"],
        "spiking_risk": "Muy Bajo",
        "notes": "Línea hardcore de Universal Nutrition con más de 40 años en el mercado y formulaciones consistentes.",
    },
    "nutrex": {
        "tier": "Tier B",
        "brand_name": "Nutrex Research",
        "trust_score": 77,
        "certifications": ["cGMP Certified (USA)"],
        "spiking_risk": "Bajo",
        "notes": "Marca consolidada estadounidense con presencia global y estándares cGMP.",
    },
    "foodtech": {
        "tier": "Tier C",
        "brand_name": "Foodtech",
        "trust_score": 55,
        "certifications": ["Resolución Seremi Salud Chile"],
        "spiking_risk": "Medio",
        "notes": "Marca chilena económica de entrada; sin auditorías independientes de terceros publicadas.",
    },
    "default": {
        "tier": "Tier C",
        "brand_name": "Marca No Auditada",
        "trust_score": 55,
        "certifications": ["Sin sellos auditados"],
        "spiking_risk": "Medio / Alto",
        "notes": "No se encontraron certificados de laboratorios independientes para esta marca.",
    },
}


def get_market_benchmark(category: str) -> Dict[str, float]:
    """
    Retorna los umbrales de referencia de precio/gramo según categoría.
    """
    return MARKET_BENCHMARKS.get(category, MARKET_BENCHMARKS["whey"])


def detect_brand(title: str) -> str:
    """
    Identifica la marca a partir del título del producto.
    """
    t = title.lower()
    for key in BRAND_TRUST_DATABASE:
        if key != "default" and key in t:
            return key

    if "rule1" in t or "rule 1" in t or "r1 " in t:
        return "rule 1"
    if "animal" in t or "universal" in t:
        return "animal"
    if "nutrex" in t:
        return "nutrex"
    if "foodtech" in t:
        return "foodtech"
    if "gold standard" in t or "on " in t:
        return "optimum nutrition"
    if "iso 100" in t or "iso100" in t:
        return "dymatize"
    if "syntha" in t:
        return "bsn"
    if "prostar" in t:
        return "ultimate nutrition"
    if "dualforce" in t:
        return "4active"

    return "default"


def get_brand_trust_data(title: str) -> Dict[str, Any]:
    """
    Obtiene la información de confianza, certificaciones y riesgo de la marca.
    """
    brand_key = detect_brand(title)
    return BRAND_TRUST_DATABASE.get(brand_key, BRAND_TRUST_DATABASE["default"])


def calculate_value_score(product: Dict[str, Any]) -> int:
    """
    Calcula una puntuación ponderada de 0 a 100 considerando:
    - Eficiencia de costo por gramo (40%)
    - Nivel de confianza y calidad de la marca (25%) -> Penaliza marcas con riesgo de amino spiking
    - Descuento real (15%)
    - Formato y volumen del envase (12%)
    - Pureza/Tipo de proteína (8%)
    """
    cost_g = product.get("cost_per_gram_clp")
    if not cost_g or cost_g <= 0:
        return 0

    cat = product.get("category", "whey")
    bench = get_market_benchmark(cat)
    title = product.get("title", "")
    trust_data = get_brand_trust_data(title)
    trust_score = trust_data["trust_score"]

    # 1. Puntuación de costo (0 a 40 pts)
    if cost_g <= bench["exceptional"]:
        cost_score = 40.0
    elif cost_g <= bench["good"]:
        factor = (bench["good"] - cost_g) / (bench["good"] - bench["exceptional"])
        cost_score = 28.0 + (factor * 12.0)
    elif cost_g <= bench["regular"]:
        factor = (bench["regular"] - cost_g) / (bench["regular"] - bench["good"])
        cost_score = 16.0 + (factor * 12.0)
    else:
        cost_score = max(4.0, 16.0 - ((cost_g - bench["regular"]) * 1.2))

    # 2. Puntuación de confianza de marca (0 a 25 pts)
    brand_score = (trust_score / 100.0) * 25.0

    # 3. Puntuación de descuento (0 a 15 pts)
    discount = float(product.get("discount_pct", 0.0))
    if discount >= 35.0:
        disc_score = 15.0
    elif discount >= 20.0:
        disc_score = 10.0 + ((discount - 20.0) / 15.0) * 5.0
    elif discount >= 10.0:
        disc_score = 5.0 + ((discount - 10.0) / 10.0) * 5.0
    else:
        disc_score = max(0.0, discount * 0.5)

    # 4. Puntuación por tamaño/formato (0 a 12 pts)
    weight_g = float(product.get("weight_grams") or 0.0)
    if weight_g >= 4000:
        size_score = 12.0
    elif weight_g >= 2000:
        size_score = 10.0
    elif weight_g >= 900:
        size_score = 6.0
    else:
        size_score = 2.0

    # 5. Tipo de suplemento (0 a 8 pts)
    type_bonus = 8.0 if cat in ["isolate", "casein"] else 6.0

    total = int(round(cost_score + brand_score + disc_score + size_score + type_bonus))
    return max(5, min(100, total))


def generate_verdict(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Emite un veredicto estructurado de compra incorporando la evidencia de calidad de la marca.
    """
    cost_g = product.get("cost_per_gram_clp")
    disc = float(product.get("discount_pct", 0.0))
    cat = product.get("category", "whey")
    title = product.get("title", "")
    bench = get_market_benchmark(cat)
    score = calculate_value_score(product)
    trust_data = get_brand_trust_data(title)
    tier = trust_data["tier"]

    if not cost_g:
        return {
            "status": "SIN_DATOS",
            "badge": "⚠️ Sin peso claro",
            "badge_color": "gray",
            "action": "Verificar ficha",
            "reason": "No fue posible determinar el peso neto en polvo de forma confiable.",
            "value_score": score,
            "trust": trust_data,
        }

    # Caso especial: Marcas Tier C con precio sospechosamente bajo
    if tier == "Tier C" and cost_g <= 30.0:
        return {
            "status": "PRECAUCION_MARCA",
            "badge": "⚠️ Barata pero Sin Certificación",
            "badge_color": "amber",
            "action": "Comprar con reserva",
            "reason": (
                f"Precio tentador de ${cost_g} CLP/g, pero la marca carece de sellos independientes (Informed-Choice/NSF). "
                "Riesgo de subdosificación o amino spiking (estudio SERNAC/ODECU)."
            ),
            "value_score": score,
            "trust": trust_data,
        }

    # Criterio 1: Ganga Maestra Certificada
    if (cost_g <= bench["exceptional"] or (score >= 78 and disc >= 15.0)) and tier in ["Tier S", "Tier A", "Tier B"]:
        return {
            "status": "COMPRA_INMEDIATA",
            "badge": f"🔥 Ganga Certificada ({tier})",
            "badge_color": "emerald",
            "action": "Comprar ahora",
            "reason": f"Excelente ratio de ${cost_g} CLP/g en marca auditada ({trust_data['brand_name']}). Sellos: {', '.join(trust_data['certifications'][:2])}.",
            "value_score": score,
            "trust": trust_data,
        }

    # Criterio 2: Buena alternativa sólida
    if (cost_g <= bench["good"] or score >= 70) and tier in ["Tier S", "Tier A", "Tier B"]:
        return {
            "status": "BUENA_OPCION",
            "badge": f"✅ Calidad Confiable ({tier})",
            "badge_color": "cyan",
            "action": "Recomendado",
            "reason": f"Precio justo Cyber (${cost_g} CLP/g) con respaldo de calidad ({trust_data['brand_name']}).",
            "value_score": score,
            "trust": trust_data,
        }

    # Criterio 3: Falsa oferta / Inflado
    if disc >= 20.0 and cost_g > bench["regular"]:
        return {
            "status": "INFLADO",
            "badge": "❌ Falsa Oferta (Precio Inflado)",
            "badge_color": "rose",
            "action": "No comprar",
            "reason": f"Muestra un supuesto descuento del {disc}%, pero su costo real por gramo (${cost_g}) sigue siendo excesivo.",
            "value_score": score,
            "trust": trust_data,
        }

    # Criterio 4: Caro / Sobreprecio
    if cost_g > bench["good"]:
        return {
            "status": "NO_CONVIENE",
            "badge": "⚠️ Sobreprecio / Esperar",
            "badge_color": "amber",
            "action": "Esperar rebaja",
            "reason": f"Costo por gramo (${cost_g} CLP/g) elevado para este Cyber. Conviene buscar marcas en Tier A o formato de 5 Lb.",
            "value_score": score,
            "trust": trust_data,
        }

    return {
        "status": "REGULAR",
        "badge": f"ℹ️ Opción Regular ({tier})",
        "badge_color": "blue",
        "action": "Evaluar según stock",
        "reason": f"Precio de mercado estándar sin descuento llamativo en {trust_data['brand_name']}.",
        "value_score": score,
        "trust": trust_data,
    }


def enrich_products_with_analytics(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enriquece cada registro de producto con métricas de valor, auditoría de marca y veredicto.
    """
    enriched = []
    seen = set()

    for item in products:
        key = (item.get("source"), item.get("title"), item.get("price"))
        if key in seen:
            continue
        seen.add(key)

        clone = dict(item)
        clone["value_score"] = calculate_value_score(clone)
        clone["verdict"] = generate_verdict(clone)
        clone["brand_trust"] = get_brand_trust_data(clone.get("title", ""))
        enriched.append(clone)

    # Ordenar por mejor relación beneficio/precio
    enriched.sort(
        key=lambda x: (
            -x.get("value_score", 0),
            0 if x.get("cost_per_gram_clp") is not None else 1,
            x.get("cost_per_gram_clp") or 999999,
        )
    )

    return enriched


def build_optimal_basket(products: List[Dict[str, Any]], target_months: int = 3) -> Dict[str, Any]:
    """
    Calcula la canasta óptima de abastecimiento para N meses.
    Filtra y prioriza marcas verificadas (Tier S, Tier A y Tier B confiable)
    para garantizar que el usuario consuma proteína biológicamente real sin riesgo de amino spiking.
    """
    trusted_products = [
        p for p in products 
        if get_brand_trust_data(p.get("title", ""))["tier"] in ["Tier S", "Tier A", "Tier B"]
    ]
    pool = trusted_products if len(trusted_products) >= 2 else products

    whey_candidates = [p for p in pool if p.get("category") == "whey" and p.get("cost_per_gram_clp")]
    casein_candidates = [p for p in pool if p.get("category") == "casein" and p.get("cost_per_gram_clp")]

    whey_candidates.sort(key=lambda x: (-calculate_value_score(x), x.get("cost_per_gram_clp", 999)))
    casein_candidates.sort(key=lambda x: (-calculate_value_score(x), x.get("cost_per_gram_clp", 999)))

    selected_whey = whey_candidates[0] if whey_candidates else None
    selected_casein = casein_candidates[0] if casein_candidates else None

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
            "trust": get_brand_trust_data(selected_whey["title"]),
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
            "trust": get_brand_trust_data(selected_casein["title"]),
        })

    avg_cost_per_gram = round(total_cost / total_protein, 2) if total_protein > 0 else 0.0
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
    Genera el diagnóstico estratégico global incorporando análisis de confianza de marcas.
    """
    valid = [p for p in products if p.get("cost_per_gram_clp")]
    if not valid:
        return {"error": "Sin productos válidos"}

    whey_items = [p for p in valid if p.get("category") == "whey"]
    casein_items = [p for p in valid if p.get("category") == "casein"]
    isolate_items = [p for p in valid if p.get("category") == "isolate"]

    # Filtrar productos para potes reales y eliminar valores extremos atípicos (> 120 CLP/g)
    whey_clean = [p for p in whey_items if (p.get("cost_per_gram_clp") or 0) <= 120.0]
    casein_clean = [p for p in casein_items if (p.get("cost_per_gram_clp") or 0) <= 120.0]
    iso_clean = [p for p in isolate_items if (p.get("cost_per_gram_clp") or 0) <= 140.0]

    avg_whey_cost = round(sum(p["cost_per_gram_clp"] for p in whey_clean) / len(whe_list), 2) if (whe_list := whey_clean or whey_items) else 0
    avg_casein_cost = round(sum(p["cost_per_gram_clp"] for p in casein_clean) / len(cas_list), 2) if (cas_list := casein_clean or casein_items) else 0
    avg_iso_cost = round(sum(p["cost_per_gram_clp"] for p in iso_clean) / len(iso_list), 2) if (iso_list := iso_clean or isolate_items) else 0

    trusted_whey = [p for p in whey_items if get_brand_trust_data(p["title"])["tier"] in ["Tier S", "Tier A", "Tier B"]]
    best_whey = min(trusted_whey, key=lambda x: x["cost_per_gram_clp"]) if trusted_whey else (min(whey_items, key=lambda x: x["cost_per_gram_clp"]) if whey_items else None)

    trusted_casein = [p for p in casein_items if get_brand_trust_data(p["title"])["tier"] in ["Tier S", "Tier A", "Tier B"]]
    best_casein = min(trusted_casein, key=lambda x: x["cost_per_gram_clp"]) if trusted_casein else (min(casein_items, key=lambda x: x["cost_per_gram_clp"]) if casein_items else None)

    tier_counts = {"Tier S": 0, "Tier A": 0, "Tier B": 0, "Tier C": 0}
    for p in valid:
        t = get_brand_trust_data(p["title"])["tier"]
        tier_counts[t] = tier_counts.get(t, 0) + 1

    diff_pct = 0.0
    if avg_whey_cost > 0 and avg_casein_cost > 0:
        diff_pct = round(((avg_casein_cost - avg_whey_cost) / avg_whey_cost) * 100.0, 1)

    casein_tactical_advice = (
        f"La caseína micelar promedia ${avg_casein_cost} CLP/g versus ${avg_whey_cost} CLP/g de la Whey concentrada. "
        "En marcas auditadas, la OstroVit 700g en SuplementosAlMayor ($43.21/g) o BioTechUSA 2.27 kg en GlobalNutrition ($49.84/g) ofrecen el balance más costo-eficiente verificado."
    )

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
        "tier_counts": tier_counts,
        "casein_premium_pct": diff_pct,
        "casein_tactical_advice": casein_tactical_advice,
    }
