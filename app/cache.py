import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import requests

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
)


def load_cache(filepath: Path) -> Dict[str, Any]:
    """
    Carga el estado de caché persistido en disco.
    """
    if not filepath.exists():
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Aviso Caché] Error al leer {filepath}: {e}")
        return {}


def save_cache(cache_data: Dict[str, Any], filepath: Path) -> None:
    """
    Guarda el estado de caché en disco de forma atómica.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    temp_file = filepath.with_suffix(".tmp")
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        temp_file.replace(filepath)
    except Exception as e:
        print(f"[Aviso Caché] Error al guardar {filepath}: {e}")
        if temp_file.exists():
            temp_file.unlink()


def compute_content_hash(content: str) -> str:
    """
    Calcula el hash SHA-256 de una respuesta para detectar cambios reales en el catálogo.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def fetch_url_conditional(
    url: str,
    cache_store: Dict[str, Any],
    timeout_sec: int = 10,
    headers: Optional[Dict[str, str]] = None,
) -> Tuple[Optional[str], bool, int]:
    """
    Descarga una URL de manera condicional usando ETag, If-Modified-Since y SHA-256.
    
    Retorna una tupla: (contenido_str, fue_actualizado_bool, status_code_int)
    - Si el servidor devuelve 304 (Not Modified), retorna el contenido en caché con fue_actualizado=False.
    - Si el contenido cambió, retorna el nuevo contenido con fue_actualizado=True y actualiza el caché.
    """
    req_headers = {"User-Agent": DEFAULT_USER_AGENT}
    if headers:
        req_headers.update(headers)

    cached_entry = cache_store.get(url, {})

    # Agregar encabezados condicionales si existen en caché
    if cached_entry.get("etag"):
        req_headers["If-None-Match"] = cached_entry["etag"]
    if cached_entry.get("last_modified"):
        req_headers["If-Modified-Since"] = cached_entry["last_modified"]

    try:
        response = requests.get(url, headers=req_headers, timeout=timeout_sec)
    except Exception as e:
        print(f"[Aviso Red] Error al consultar {url}: {e}")
        # Si falla la red pero tenemos caché previo, retornamos el caché
        if cached_entry.get("content"):
            return cached_entry["content"], False, 0
        return None, False, 0

    # Caso 1: Servidor responde 304 Not Modified (ahorro 100% de datos)
    if response.status_code == 304:
        cache_store[url]["last_checked"] = int(time.time())
        return cached_entry.get("content"), False, 304

    # Caso 2: Error del servidor
    if response.status_code not in [200, 206]:
        return None, False, response.status_code

    content_text = response.text
    new_hash = compute_content_hash(content_text)

    # Caso 3: Servidor devolvió 200 pero el hash de contenido es idéntico al previo
    if cached_entry.get("content_hash") == new_hash:
        cache_store[url]["last_checked"] = int(time.time())
        return cached_entry.get("content"), False, response.status_code

    # Caso 4: Contenido nuevo o modificado (guardar en caché)
    cache_store[url] = {
        "etag": response.headers.get("ETag"),
        "last_modified": response.headers.get("Last-Modified"),
        "content_hash": new_hash,
        "content": content_text,
        "last_checked": int(time.time()),
    }

    return content_text, True, response.status_code
