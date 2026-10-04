import json
import urllib.parse
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from app.cache import fetch_url_conditional
from app.normalization import (
    is_valid_powder_supplement,
    extract_weight_grams,
    detect_protein_category,
    estimate_protein_grams,
    calculate_cost_per_gram,
    calculate_discount,
    parse_clean_price,
    normalize_product_record,
)


def extract_shopify_suggest(
    store_name: str,
    base_url: str,
    queries: List[str],
    cache_store: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extrae productos usando el endpoint /search/suggest.json de Shopify con caché condicional.
    """
    results: List[Dict[str, Any]] = []

    for q in queries:
        encoded_q = urllib.parse.quote(q)
        url = f"{base_url.rstrip('/')}/search/suggest.json?q={encoded_q}&resources[type]=product"
        content, updated, status = fetch_url_conditional(url, cache_store)
        if not content:
            continue

        try:
            data = json.loads(content)
        except Exception:
            continue

        items = data.get("resources", {}).get("results", {}).get("products", [])
        for it in items:
            title = it.get("title", "")
            if not is_valid_powder_supplement(title):
                continue

            price_raw = it.get("price")
            compare_at_raw = it.get("compare_at_price_max") or it.get("compare_at_price")

            try:
                price = float(price_raw) if price_raw else 0.0
                if price > 500000:
                    price = price / 100.0
            except (ValueError, TypeError):
                continue

            try:
                orig_price = float(compare_at_raw) if compare_at_raw else None
                if orig_price and orig_price > 500000:
                    orig_price = orig_price / 100.0
            except (ValueError, TypeError):
                orig_price = None

            if price <= 0:
                continue

            raw_url = it.get("url", "")
            permalink = f"{base_url.rstrip('/')}{raw_url}" if raw_url.startswith("/") else raw_url

            record = normalize_product_record(
                source=store_name,
                title=title,
                price=price,
                original_price=orig_price,
                permalink=permalink,
                available=True,
            )
            results.append(record)

    return results


def extract_vtex(
    store_name: str,
    base_url: str,
    terms: List[str],
    cache_store: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extrae productos desde tiendas con catálogo VTEX (ej. Supletech) con caché condicional.
    """
    results: List[Dict[str, Any]] = []

    for term in terms:
        encoded_term = urllib.parse.quote(term)
        url = f"{base_url.rstrip('/')}/api/catalog_system/pub/products/search?ft={encoded_term}"
        content, updated, status = fetch_url_conditional(url, cache_store)
        if not content:
            continue

        try:
            products_data = json.loads(content)
        except Exception:
            continue

        if not isinstance(products_data, list):
            continue

        for prod in products_data:
            product_name = prod.get("productName", "")
            link = prod.get("link", "")
            items = prod.get("items", [])

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
                record = normalize_product_record(
                    source=store_name,
                    title=name,
                    price=price,
                    original_price=original_price,
                    permalink=link,
                    available=True,
                )
                results.append(record)

    return results


def extract_jumpseller(
    store_name: str,
    base_url: str,
    queries: List[str],
    cache_store: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extrae productos desde tiendas Jumpseller (ej. OutletFit) parseando HTML con caché condicional.
    """
    results: List[Dict[str, Any]] = []

    for q in queries:
        encoded_q = urllib.parse.quote(q)
        url = f"{base_url.rstrip('/')}/search/{encoded_q}"
        content, updated, status = fetch_url_conditional(url, cache_store)
        if not content:
            continue

        soup = BeautifulSoup(content, "html.parser")
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
            raw_href = anchor.get("href", "")
            permalink = f"{base_url.rstrip('/')}{raw_href}" if raw_href.startswith("/") else raw_href

            record = normalize_product_record(
                source=store_name,
                title=title,
                price=price,
                original_price=original_price,
                permalink=permalink,
                available=True,
            )
            results.append(record)

    return results


def extract_bsale(
    store_name: str,
    base_url: str,
    paths: List[str],
    cache_store: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extrae productos desde tiendas Bsale (ej. Strongest) con caché condicional.
    """
    import re
    results: List[Dict[str, Any]] = []

    for path in paths:
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        content, updated, status = fetch_url_conditional(url, cache_store)
        if not content:
            continue

        soup = BeautifulSoup(content, "html.parser")
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

            prices_found = re.findall(r"\$\s*(\d{1,3}(?:\.\d{3})+)", text)
            if not prices_found:
                continue

            prices_num = [parse_clean_price(p) for p in prices_found if parse_clean_price(p)]
            if not prices_num:
                continue

            price = min(prices_num)
            original_price = max(prices_num) if len(prices_num) > 1 and max(prices_num) > price else None

            title = a.get_text(strip=True)
            if not title or len(title) < 5 or "$" in title:
                title = text.split("$")[0].strip()

            if not is_valid_powder_supplement(title):
                continue

            permalink = f"{base_url.rstrip('/')}{href}" if href.startswith("/") else href
            record = normalize_product_record(
                source=store_name,
                title=title,
                price=price,
                original_price=original_price,
                permalink=permalink,
                available=True,
            )
            results.append(record)

    return results


def extract_woocommerce(
    store_name: str,
    base_url: str,
    paths: List[str],
    cache_store: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Extrae productos desde tiendas WooCommerce (ej. ChileSuplementos) con caché condicional.
    """
    import re
    results: List[Dict[str, Any]] = []

    for path in paths:
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        content, updated, status = fetch_url_conditional(url, cache_store)
        if not content:
            continue

        soup = BeautifulSoup(content, "html.parser")
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

            title = text.split("$")[0]
            for prefix in ["Ahorras", "Más Vendido", "Nuevo", "Regalos"]:
                title = title.replace(prefix, "")
            title = title.strip()

            if not is_valid_powder_supplement(title):
                continue

            record = normalize_product_record(
                source=store_name,
                title=title,
                price=price,
                original_price=original_price,
                permalink=href,
                available=True,
            )
            results.append(record)

    return results


def scrape_all_stores(
    stores_catalog: List[Dict[str, Any]],
    search_queries: List[str],
    cache_store: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Coordina la extracción de todas las tiendas configuradas delegando en el extractor correspondiente.
    """
    all_products: List[Dict[str, Any]] = []

    for store in stores_catalog:
        name = store["name"]
        stype = store["type"]
        url = store["url"]

        try:
            if stype == "shopify":
                extracted = extract_shopify_suggest(name, url, search_queries, cache_store)
            elif stype == "vtex":
                terms = store.get("terms", search_queries)
                extracted = extract_vtex(name, url, terms, cache_store)
            elif stype == "jumpseller":
                queries = store.get("queries", search_queries)
                extracted = extract_jumpseller(name, url, queries, cache_store)
            elif stype == "bsale":
                paths = store.get("paths", ["/collection/proteinas"])
                extracted = extract_bsale(name, url, paths, cache_store)
            elif stype == "woocommerce":
                paths = store.get("paths", [])
                extracted = extract_woocommerce(name, url, paths, cache_store)
            else:
                extracted = []

            all_products.extend(extracted)
        except Exception as e:
            print(f"[Aviso Extractor] Fallo al extraer de {name}: {e}")

    return all_products
