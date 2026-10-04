import re
from typing import Optional, List, Dict, Any
import requests

LBS_TO_GRAMS = 453.592
KG_TO_GRAMS = 1000.0

PROTEIN_PURITY_RATIOS = {
    "isolate": 0.86,
    "whey": 0.73,
    "casein": 0.76,
    "default": 0.73,
}

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
    Filtra productos que no son proteína en polvo (ej. shakers, bebidas listas, barras).
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
    Soporta patrones en lbs, libras, kg, kilos y gramos (g).
    """
    if not title:
        return None

    text = title.lower().replace(",", ".")

    # Buscar libras: ej. "5 lbs", "5lb", "5.5 libras"
    match_lbs = re.search(r"(\d+(?:\.\d+)?)\s*(?:lbs?|libras?)\b", text)
    if match_lbs:
        val = float(match_lbs.group(1))
        return round(val * LBS_TO_GRAMS, 1)

    # Buscar kilogramos: ej. "2.27 kg", "2kg", "2 kilos"
    match_kg = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilos?)\b", text)
    if match_kg:
        val = float(match_kg.group(1))
        return round(val * KG_TO_GRAMS, 1)

    # Buscar gramos: ej. "908g", "908 g", "1000 grs"
    match_g = re.search(r"(\d+(?:\.\d+)?)\s*(?:g|gr|grs|gramos)\b", text)
    if match_g:
        val = float(match_g.group(1))
        return round(val, 1)

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


def parse_vtex_product(product: Dict[str, Any], store_name: str) -> List[Dict[str, Any]]:
    """
    Parsea productos de tiendas basadas en VTEX (ej. Supletech).
    """
    parsed_items = []
    product_name = product.get("productName", "")
    link = product.get("link", "")
    items = product.get("items", [])

    for item in items:
        name = item.get("nameComplete") or f"{product_name} {item.get('name', '')}"
        if not is_valid_powder_supplement(name):
            continue

        sellers = item.get("sellers", [])
        if not sellers:
            continue

        comm = sellers[0].get("commertialOffer", {})
        price = comm.get("Price", 0.0)
        list_price = comm.get("ListPrice", 0.0)
        avail = comm.get("AvailableQuantity", 0)

        if price <= 0 or avail <= 0:
            continue

        original_price = list_price if list_price > price else None
        discount = calculate_discount(original_price, price)
        weight_g = extract_weight_grams(name)
        category = detect_protein_category(name)

        net_protein_g = estimate_protein_grams(weight_g, category) if weight_g else None
        cost_per_g = calculate_cost_per_gram(price, net_protein_g) if net_protein_g else None

        parsed_items.append({
            "source": store_name,
            "title": name,
            "price": price,
            "original_price": original_price,
            "discount_pct": discount,
            "category": category,
            "weight_grams": weight_g,
            "net_protein_grams": net_protein_g,
            "cost_per_gram_clp": cost_per_g,
            "permalink": link,
            "available": True,
        })

    return parsed_items


def parse_shopify_product(product: Dict[str, Any], store_name: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Parsea productos de tiendas basadas en Shopify (ej. /products.json).
    """
    parsed_items = []
    title = product.get("title", "")
    handle = product.get("handle", "")
    variants = product.get("variants", [])

    for variant in variants:
        variant_title = variant.get("title", "")
        full_title = f"{title} - {variant_title}" if variant_title != "Default Title" else title
        if not is_valid_powder_supplement(full_title):
            continue

        price_raw = variant.get("price")
        compare_at_raw = variant.get("compare_at_price")

        try:
            price = float(price_raw) if price_raw else 0.0
        except (ValueError, TypeError):
            continue

        try:
            original_price = float(compare_at_raw) if compare_at_raw else None
        except (ValueError, TypeError):
            original_price = None

        if price <= 0:
            continue

        weight_g = extract_weight_grams(full_title)
        if not weight_g and variant.get("grams"):
            try:
                g = float(variant["grams"])
                if g >= 400:  # evitar potes pequeños/muestras
                    weight_g = g
            except (ValueError, TypeError):
                pass

        category = detect_protein_category(full_title)
        net_protein_g = estimate_protein_grams(weight_g, category) if weight_g else None
        cost_per_g = calculate_cost_per_gram(price, net_protein_g) if net_protein_g else None
        discount = calculate_discount(original_price, price)
        permalink = f"{base_url.rstrip('/')}/products/{handle}"

        parsed_items.append({
            "source": store_name,
            "title": full_title,
            "price": price,
            "original_price": original_price,
            "discount_pct": discount,
            "category": category,
            "weight_grams": weight_g,
            "net_protein_grams": net_protein_g,
            "cost_per_gram_clp": cost_per_g,
            "permalink": permalink,
            "available": variant.get("available", True),
        })

    return parsed_items


def parse_shopify_suggest_item(item: Dict[str, Any], store_name: str, base_url: str) -> Optional[Dict[str, Any]]:
    """
    Parsea productos devueltos por el endpoint /search/suggest.json de Shopify.
    """
    title = item.get("title", "")
    if not is_valid_powder_supplement(title):
        return None

    price_raw = item.get("price")
    compare_at_raw = item.get("compare_at_price_max") or item.get("compare_at_price")

    try:
        # Algunos endpoints entregan el precio en centavos (ej. 3499000 -> 34990) si es > 1.000.000
        price = float(price_raw) if price_raw else 0.0
        if price > 500000:
            price = price / 100.0
    except (ValueError, TypeError):
        return None

    try:
        original_price = float(compare_at_raw) if compare_at_raw else None
        if original_price and original_price > 500000:
            original_price = original_price / 100.0
    except (ValueError, TypeError):
        original_price = None

    if price <= 0:
        return None

    weight_g = extract_weight_grams(title)
    category = detect_protein_category(title)
    net_protein_g = estimate_protein_grams(weight_g, category) if weight_g else None
    cost_per_g = calculate_cost_per_gram(price, net_protein_g) if net_protein_g else None
    discount = calculate_discount(original_price, price)

    raw_url = item.get("url", "")
    permalink = f"{base_url.rstrip('/')}{raw_url}" if raw_url.startswith("/") else raw_url

    return {
        "source": store_name,
        "title": title,
        "price": price,
        "original_price": original_price,
        "discount_pct": discount,
        "category": category,
        "weight_grams": weight_g,
        "net_protein_grams": net_protein_g,
        "cost_per_gram_clp": cost_per_g,
        "permalink": permalink,
        "available": True,
    }


def filter_and_rank_deals(
    products: List[Dict[str, Any]],
    target_categories: Optional[List[str]] = None,
    max_cost_per_gram: Optional[float] = None,
    min_discount_pct: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Filtra y ordena los productos por mejor costo por gramo de proteína o descuento.
    """
    categories = set(target_categories or ["whey", "casein", "isolate"])
    filtered = []
    seen = set()

    for item in products:
        key = (item.get("source"), item.get("title"), item.get("price"))
        if key in seen:
            continue
        seen.add(key)

        if item["category"] not in categories:
            continue

        if min_discount_pct > 0 and item["discount_pct"] < min_discount_pct:
            continue

        cost_g = item.get("cost_per_gram_clp")
        if max_cost_per_gram is not None:
            if cost_g is None or cost_g > max_cost_per_gram:
                continue

        filtered.append(item)

    filtered.sort(
        key=lambda x: (
            0 if x.get("cost_per_gram_clp") is not None else 1,
            x.get("cost_per_gram_clp") or 999999,
            -x.get("discount_pct", 0),
        )
    )

    return filtered


def fetch_vtex_products(store_name: str, base_url: str, terms: List[str]) -> List[Dict[str, Any]]:
    """
    Consulta productos desde tiendas VTEX (ej. Supletech).
    """
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for term in terms:
        url = f"{base_url.rstrip('/')}/api/catalog_system/pub/products/search?ft={term}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code in [200, 206]:
                data = resp.json()
                for prod in data:
                    results.extend(parse_vtex_product(prod, store_name))
        except Exception as e:
            print(f"[Aviso] Error al consultar VTEX {store_name} ({term}): {e}")

    return results


def fetch_shopify_suggest_products(store_name: str, base_url: str, queries: List[str]) -> List[Dict[str, Any]]:
    """
    Consulta el endpoint de sugerencias y búsqueda de Shopify (ej. All Nutrition, Winkler).
    """
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for q in queries:
        url = f"{base_url.rstrip('/')}/search/suggest.json?q={requests.utils.quote(q)}&resources[type]=product"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("resources", {}).get("results", {}).get("products", [])
                for it in items:
                    parsed = parse_shopify_suggest_item(it, store_name, base_url)
                    if parsed:
                        results.append(parsed)
        except Exception as e:
            print(f"[Aviso] Error al consultar Shopify {store_name} ({q}): {e}")

    return results


def parse_clean_price(price_str: str) -> Optional[float]:
    """
    Limpia cadenas como '$ 42.990' o '$42990' a float.
    """
    if not price_str:
        return None
    cleaned = re.sub(r"[^\d]", "", price_str)
    try:
        val = float(cleaned)
        return val if val > 0 else None
    except ValueError:
        return None


def fetch_jumpseller_products(store_name: str, base_url: str, queries: List[str]) -> List[Dict[str, Any]]:
    """
    Scraper para tiendas basadas en Jumpseller (ej. OutletFit).
    """
    from bs4 import BeautifulSoup
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for q in queries:
        url = f"{base_url.rstrip('/')}/search/{requests.utils.quote(q)}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".product-block")

            for card in cards:
                anchor = card.select_one("a.product-block__anchor")
                title = anchor.get("title", "") if anchor else ""
                title = title.replace("Ir a ", "").strip()
                if not title or not is_valid_powder_supplement(title):
                    continue

                price_new = card.select_one(".product-block__price--new")
                price_old = card.select_one(".product-block__price--old")

                price = parse_clean_price(price_new.get_text() if price_new else None)
                if not price or price <= 0:
                    continue

                original_price = parse_clean_price(price_old.get_text() if price_old else None)
                discount = calculate_discount(original_price, price)
                weight_g = extract_weight_grams(title)
                category = detect_protein_category(title)
                net_protein_g = estimate_protein_grams(weight_g, category) if weight_g else None
                cost_per_g = calculate_cost_per_gram(price, net_protein_g) if net_protein_g else None

                raw_href = anchor.get("href", "")
                permalink = f"{base_url.rstrip('/')}{raw_href}" if raw_href.startswith("/") else raw_href

                results.append({
                    "source": store_name,
                    "title": title,
                    "price": price,
                    "original_price": original_price,
                    "discount_pct": discount,
                    "category": category,
                    "weight_grams": weight_g,
                    "net_protein_grams": net_protein_g,
                    "cost_per_gram_clp": cost_per_g,
                    "permalink": permalink,
                    "available": True,
                })
        except Exception as e:
            print(f"[Aviso] Error al consultar Jumpseller {store_name} ({q}): {e}")

    return results


def fetch_bsale_products(store_name: str, base_url: str, collection_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Scraper para tiendas basadas en Bsale (ej. Strongest.cl).
    """
    from bs4 import BeautifulSoup
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for path in collection_paths:
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

            seen_urls = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/product/" not in href or href in seen_urls:
                    continue
                seen_urls.add(href)

                parent = a.find_parent("div")
                if not parent:
                    continue
                text = parent.get_text(" ", strip=True)
                if "$" not in text:
                    continue

                # Extraer precios con formato CLP ej: $ 64.990 o $ 72.990
                prices_found = re.findall(r"\$\s*(\d{1,3}(?:\.\d{3})+)", text)
                if not prices_found:
                    continue

                prices_num = [parse_clean_price(p) for p in prices_found if parse_clean_price(p)]
                if not prices_num:
                    continue

                # El precio menor es el actual si hay oferta
                price = min(prices_num)
                original_price = max(prices_num) if len(prices_num) > 1 and max(prices_num) > price else None

                # Extraer título del enlace o texto
                title = a.get_text(strip=True)
                if not title or len(title) < 5 or "$" in title:
                    # Limpiar texto del contenedor
                    title = text.split("$")[0].strip()

                if not is_valid_powder_supplement(title):
                    continue

                discount = calculate_discount(original_price, price)
                weight_g = extract_weight_grams(title)
                category = detect_protein_category(title)
                net_protein_g = estimate_protein_grams(weight_g, category) if weight_g else None
                cost_per_g = calculate_cost_per_gram(price, net_protein_g) if net_protein_g else None

                permalink = f"{base_url.rstrip('/')}{href}" if href.startswith("/") else href

                results.append({
                    "source": store_name,
                    "title": title,
                    "price": price,
                    "original_price": original_price,
                    "discount_pct": discount,
                    "category": category,
                    "weight_grams": weight_g,
                    "net_protein_grams": net_protein_g,
                    "cost_per_gram_clp": cost_per_g,
                    "permalink": permalink,
                    "available": True,
                })
        except Exception as e:
            print(f"[Aviso] Error al consultar Bsale {store_name} ({path}): {e}")

    return results


def fetch_woocommerce_html_products(store_name: str, base_url: str, category_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Scraper HTML para tiendas WooCommerce con navegación por categorías (ej. ChileSuplementos).
    """
    from bs4 import BeautifulSoup
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for path in category_paths:
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

            seen_links = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/producto/" not in href or href in seen_links:
                    continue
                seen_links.add(href)

                text = a.get_text(" ", strip=True)
                prices_found = re.findall(r"\$\s*(\d{1,3}(?:\.\d{3})+)", text)
                if not prices_found:
                    continue

                prices_num = [parse_clean_price(p) for p in prices_found if parse_clean_price(p)]
                if not prices_num:
                    continue

                price = prices_num[-1]
                original_price = prices_num[0] if len(prices_num) > 1 and prices_num[0] > price else None

                # Limpiar el título removiendo prefijos comunes de tienda
                title = text.split("$")[0]
                for prefix in ["Ahorras", "Más Vendido", "Nuevo", "Regalos"]:
                    title = title.replace(prefix, "")
                title = title.strip()

                if not is_valid_powder_supplement(title):
                    continue

                discount = calculate_discount(original_price, price)
                weight_g = extract_weight_grams(title)
                category = detect_protein_category(title)
                net_protein_g = estimate_protein_grams(weight_g, category) if weight_g else None
                cost_per_g = calculate_cost_per_gram(price, net_protein_g) if net_protein_g else None

                results.append({
                    "source": store_name,
                    "title": title,
                    "price": price,
                    "original_price": original_price,
                    "discount_pct": discount,
                    "category": category,
                    "weight_grams": weight_g,
                    "net_protein_grams": net_protein_g,
                    "cost_per_gram_clp": cost_per_g,
                    "permalink": href,
                    "available": True,
                })
        except Exception as e:
            print(f"[Aviso] Error al consultar WooCommerce {store_name} ({path}): {e}")

    return results
