import re
from typing import Optional, Dict, Any
from app.config import LBS_TO_GRAMS, KG_TO_GRAMS, PROTEIN_PURITY_RATIOS

EXCLUDED_KEYWORDS = [
    "shaker",
    "botella",
    "mezclador",
    "water",
    "líquida",
    "liquida",
    "barra",
    "barras",
    "barrita",
    "snack",
    "cookie",
    "galleta",
    "pancakes",
    "creatina",
    "pre entreno",
    "pre-workout",
    "quemador",
]


def is_valid_powder_supplement(title: str) -> bool:
    """
    Filtra productos que no son proteína en polvo (ej. shakers, botellas, barras, creatinas).
    """
    if not title:
        return False
    lower = title.lower()
    for word in EXCLUDED_KEYWORDS:
        if word in lower:
            return False
    return True


def extract_weight_grams(title: str) -> Optional[float]:
    """
    Extrae el peso total del envase en gramos a partir del título o descripción.
    Soporta patrones en lbs, libras, kg, kilos y gramos (g/gr/grs).
    Maneja separadores de miles chilenos como '2.350 g' -> 2350 gramos.
    Filtra porciones individuales o sachets (< 350g) para no distorsionar el costo de potes.
    """
    if not title:
        return None

    text = title.lower()

    # Detectar gramos con separador de miles: ej. "2.350 g", "2.270 gr"
    match_thousands_g = re.search(r"(\d{1,2})\.(\d{3})\s*(?:g|gr|grs|gramos)\b", text)
    if match_thousands_g:
        val = float(f"{match_thousands_g.group(1)}{match_thousands_g.group(2)}")
        return round(val, 1)

    # Reemplazar comas por puntos para números decimales
    text_dec = text.replace(",", ".")

    # Buscar libras: ej. "5 lbs", "5lb", "5.5 libras"
    match_lbs = re.search(r"(\d+(?:\.\d+)?)\s*(?:lbs?|libras?)\b", text_dec)
    if match_lbs:
        val = float(match_lbs.group(1))
        grams = round(val * LBS_TO_GRAMS, 1)
        return grams if grams >= 350 else None

    # Buscar kilogramos: ej. "2.27 kg", "2kg", "2 kilos"
    match_kg = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilos?)\b", text_dec)
    if match_kg:
        val = float(match_kg.group(1))
        grams = round(val * KG_TO_GRAMS, 1)
        return grams if grams >= 350 else None

    # Buscar gramos estándar: ej. "908g", "908 g", "1000 grs"
    match_g = re.search(r"(\d{3,5})\s*(?:g|gr|grs|gramos)\b", text_dec)
    if match_g:
        val = float(match_g.group(1))
        return round(val, 1) if val >= 350 else None

    return None


def parse_clean_price(price_str: Optional[str]) -> Optional[float]:
    """
    Limpia cadenas de precios como '$ 42.990' o '$42990' a float.
    """
    if not price_str:
        return None
    cleaned = re.sub(r"[^\d]", "", str(price_str))
    try:
        val = float(cleaned)
        return val if val > 0 else None
    except ValueError:
        return None


def calculate_discount(original_price: Optional[float], current_price: float) -> float:
    """
    Calcula el porcentaje de descuento si existe precio original.
    """
    if not original_price or original_price <= current_price:
        return 0.0
    discount = ((original_price - current_price) / original_price) * 100.0
    return round(discount, 1)


def detect_protein_category(text: str) -> str:
    """
    Determina si el producto es caseína, whey isolate o whey concentrado/blend.
    """
    lower = text.lower()
    if "casein" in lower or "caseina" in lower or "micellar" in lower or "micelar" in lower:
        return "casein"
    if "isolate" in lower or "iso " in lower or "iso100" in lower or "isopure" in lower:
        return "isolate"
    if "whey" in lower or "suero" in lower or "gold standard" in lower:
        return "whey"
    return "default"


def estimate_protein_grams(total_product_grams: float, category: str) -> float:
    """
    Estima los gramos netos de proteína según pureza típica del tipo de suplemento.
    """
    ratio = PROTEIN_PURITY_RATIOS.get(category, PROTEIN_PURITY_RATIOS["default"])
    return round(total_product_grams * ratio, 1)


def calculate_cost_per_gram(price: float, total_protein_grams: float) -> Optional[float]:
    """
    Calcula el costo en CLP por gramo neto de proteína.
    """
    if total_protein_grams <= 0 or price <= 0:
        return None
    return round(price / total_protein_grams, 2)


def normalize_product_record(
    source: str,
    title: str,
    price: float,
    original_price: Optional[float] = None,
    weight_g: Optional[float] = None,
    category: Optional[str] = None,
    permalink: str = "",
    available: bool = True,
) -> Dict[str, Any]:
    """
    Crea un registro de producto completamente normalizado y validado.
    """
    resolved_category = category or detect_protein_category(title)
    resolved_weight = weight_g if weight_g is not None else extract_weight_grams(title)

    net_protein = None
    cost_per_g = None
    if resolved_weight and resolved_weight > 0:
        net_protein = estimate_protein_grams(resolved_weight, resolved_category)
        cost_per_g = calculate_cost_per_gram(price, net_protein)

    discount = calculate_discount(original_price, price)

    return {
        "source": source,
        "title": title.strip(),
        "price": float(price),
        "original_price": float(original_price) if original_price else None,
        "discount_pct": discount,
        "category": resolved_category,
        "weight_grams": resolved_weight,
        "net_protein_grams": net_protein,
        "cost_per_gram_clp": cost_per_g,
        "permalink": permalink,
        "available": available,
    }
