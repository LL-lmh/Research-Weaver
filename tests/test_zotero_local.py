import json
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


class _Handler(BaseHTTPRequestHandler):
    routes = {}

    def do_GET(self):
        key = urlparse(self.path).path
        status, payload = self.routes.get(key, (404, {"error": "missing"}))
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return


def item(key, title, *, doi="", extra="Citation Key: example2026"):
    return {
        "key": key,
        "data": {
            "key": key,
            "itemType": "journalArticle",
            "title": title,
            "date": "2026-04-03",
            "DOI": doi,
            "extra": extra,
            "creators": [{"firstName": "Ada", "lastName": "Lovelace"}],
        },
    }


class ZoteroLocalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        _Handler.routes = {}

    def test_resolve_unique_query_returns_normalized_identity(self):
        _Handler.routes["/api/users/0/items/top"] = (
            200,
            [item("ABCD1234", "Graph Weaving", doi="10.1000/graph")],
        )
        from scripts.zotero_local import resolve_item

        result = resolve_item(query="Graph Weaving", item_key=None, base_url=self.base_url)

        self.assertEqual(result["item_key"], "ABCD1234")
        self.assertEqual(result["authors"], ["Ada Lovelace"])
        self.assertEqual(result["year"], "2026")
        self.assertEqual(result["doi"], "10.1000/graph")
        self.assertEqual(result["citekey"], "example2026")

    def test_resolve_query_rejects_ambiguous_matches(self):
        _Handler.routes["/api/users/0/items/top"] = (
            200,
            [item("AAAA1111", "Same"), item("BBBB2222", "Same")],
        )
        from scripts.zotero_local import ZoteroAmbiguousError, resolve_item

        with self.assertRaises(ZoteroAmbiguousError) as raised:
            resolve_item(query="Same", item_key=None, base_url=self.base_url)

        self.assertEqual(raised.exception.candidates, ["AAAA1111", "BBBB2222"])

    def test_resolve_doi_filters_exact_identifier(self):
        _Handler.routes["/api/users/0/items/top"] = (
            200,
            [
                item("WRONG001", "Similar title", doi="10.1000/other"),
                item("RIGHT001", "Target", doi="10.1000/Graph"),
            ],
        )
        from scripts.zotero_local import resolve_item

        result = resolve_item(query="https://doi.org/10.1000/graph", item_key=None, base_url=self.base_url)
        self.assertEqual(result["item_key"], "RIGHT001")

    def test_resolve_arxiv_filters_exact_identifier(self):
        first = item("WRONG001", "Similar")
        second = item("RIGHT001", "Target")
        second["data"]["extra"] += "\narXiv: 2401.12345v2"
        _Handler.routes["/api/users/0/items/top"] = (200, [first, second])
        from scripts.zotero_local import resolve_item

        result = resolve_item(query="arXiv:2401.12345v2", item_key=None, base_url=self.base_url)
        self.assertEqual(result["item_key"], "RIGHT001")

    def test_resolve_exact_item_key_uses_item_route(self):
        _Handler.routes["/api/users/0/items/ABCD1234"] = (
            200,
            item("ABCD1234", "Exact Paper"),
        )
        from scripts.zotero_local import resolve_item

        result = resolve_item(query=None, item_key="ABCD1234", base_url=self.base_url)

        self.assertEqual(result["title"], "Exact Paper")

    def test_resolve_pdf_attachment_decodes_unicode_file_url(self):
        attachment = {
            "key": "PDF12345",
            "data": {
                "key": "PDF12345",
                "itemType": "attachment",
                "contentType": "application/pdf",
                "filename": "论文 文件.pdf",
            },
        }
        _Handler.routes["/api/users/0/items/ABCD1234/children"] = (200, [attachment])
        _Handler.routes["/api/users/0/items/PDF12345/file/view/url"] = (
            200,
            "file:///C:/Zotero/storage/论文%20文件.pdf",
        )
        from scripts.zotero_local import list_children, resolve_pdf_attachment

        children = list_children("ABCD1234", self.base_url)
        result = resolve_pdf_attachment({"item_key": "ABCD1234"}, children, self.base_url)

        self.assertEqual(result["attachment_key"], "PDF12345")
        self.assertEqual(result["pdf_path"], "C:\\Zotero\\storage\\论文 文件.pdf")

    def test_resolve_pdf_attachment_preserves_unc_server(self):
        attachment = {
            "key": "PDF12345",
            "data": {
                "key": "PDF12345",
                "itemType": "attachment",
                "contentType": "application/pdf",
                "filename": "论文.pdf",
            },
        }
        _Handler.routes["/api/users/0/items/ABCD1234/children"] = (200, [attachment])
        _Handler.routes["/api/users/0/items/PDF12345/file/view/url"] = (
            200,
            "file://server/share/论文.pdf",
        )
        from scripts.zotero_local import list_children, resolve_pdf_attachment

        result = resolve_pdf_attachment(
            {"item_key": "ABCD1234"}, list_children("ABCD1234", self.base_url), self.base_url
        )
        self.assertEqual(result["pdf_path"], "\\\\server\\share\\论文.pdf")

    def test_api_unavailable_raises_connection_error(self):
        from scripts.zotero_local import ZoteroConnectionError, api_get

        with self.assertRaises(ZoteroConnectionError):
            api_get("/api/", "http://127.0.0.1:1")

    def test_cli_emits_unicode_json_as_utf8(self):
        _Handler.routes["/api/users/0/items/ABCD1234"] = (
            200,
            item("ABCD1234", "中文论文"),
        )
        attachment = {
            "key": "PDF12345",
            "data": {
                "key": "PDF12345",
                "itemType": "attachment",
                "contentType": "application/pdf",
                "filename": "论文.pdf",
            },
        }
        _Handler.routes["/api/users/0/items/ABCD1234/children"] = (200, [attachment])
        _Handler.routes["/api/users/0/items/PDF12345/file/view/url"] = (
            200,
            "file:///C:/资料/论文.pdf",
        )
        script = Path(__file__).resolve().parents[1] / "scripts" / "zotero_local.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--base-url",
                self.base_url,
                "resolve",
                "--item-key",
                "ABCD1234",
            ],
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("中文论文", result.stdout.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
