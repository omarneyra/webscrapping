import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.cache import (
    load_cache,
    save_cache,
    compute_content_hash,
    fetch_url_conditional,
)


class TestCache(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_file = Path(self.temp_dir.name) / "test_cache.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_save_cache(self):
        initial = load_cache(self.cache_file)
        self.assertEqual(initial, {})

        sample_data = {
            "https://test.cl/api": {
                "etag": "w/123",
                "content_hash": "abc",
                "content": '{"products": []}',
                "last_checked": 123456,
            }
        }
        save_cache(sample_data, self.cache_file)
        self.assertTrue(self.cache_file.exists())

        loaded = load_cache(self.cache_file)
        self.assertEqual(loaded, sample_data)

    def test_compute_content_hash(self):
        h1 = compute_content_hash("hello world")
        h2 = compute_content_hash("hello world")
        h3 = compute_content_hash("different")
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)

    @patch("requests.get")
    def test_fetch_url_conditional_304_not_modified(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 304
        mock_get.return_value = mock_resp

        store = {
            "https://example.com/api": {
                "etag": "etag-123",
                "content": "cached body",
                "content_hash": "hash123",
            }
        }

        content, updated, status = fetch_url_conditional("https://example.com/api", store)
        self.assertEqual(content, "cached body")
        self.assertFalse(updated)
        self.assertEqual(status, 304)

        # Verificar que se enviaron las cabeceras condicionales
        call_headers = mock_get.call_args[1]["headers"]
        self.assertEqual(call_headers["If-None-Match"], "etag-123")

    @patch("requests.get")
    def test_fetch_url_conditional_200_same_hash(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "identical content"
        mock_resp.headers = {"ETag": "new-etag"}
        mock_get.return_value = mock_resp

        expected_hash = compute_content_hash("identical content")
        store = {
            "https://example.com/api": {
                "content": "identical content",
                "content_hash": expected_hash,
            }
        }

        content, updated, status = fetch_url_conditional("https://example.com/api", store)
        self.assertEqual(content, "identical content")
        self.assertFalse(updated)
        self.assertEqual(status, 200)

    @patch("requests.get")
    def test_fetch_url_conditional_200_new_content(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "fresh content data"
        mock_resp.headers = {"ETag": "etag-abc"}
        mock_get.return_value = mock_resp

        store = {}
        content, updated, status = fetch_url_conditional("https://example.com/api", store)
        self.assertEqual(content, "fresh content data")
        self.assertTrue(updated)
        self.assertEqual(status, 200)
        self.assertIn("https://example.com/api", store)
        self.assertEqual(store["https://example.com/api"]["etag"], "etag-abc")


if __name__ == "__main__":
    unittest.main()
