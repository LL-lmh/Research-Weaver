import hashlib
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, urlparse

from scripts.note_store import preflight, save_note
from scripts.zotero_local import list_children, resolve_item, resolve_pdf_attachment


class _SmokeHandler(BaseHTTPRequestHandler):
    routes = {}

    def do_GET(self):
        status, payload = self.routes.get(urlparse(self.path).path, (404, {"error": "missing"}))
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return


class WorkflowSmokeTest(unittest.TestCase):
    def test_fake_zotero_to_bilingual_vault_without_copying_pdf(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            vault = root / "Obsidian Vault"
            source = root / "Zotero storage" / "论文.pdf"
            vault.mkdir()
            source.parent.mkdir()
            source.write_bytes(b"%PDF-1.4 synthetic fixture")

            item = {
                "key": "PAPER001",
                "data": {
                    "key": "PAPER001",
                    "itemType": "journalArticle",
                    "title": "Evidence to Research",
                    "date": "2026",
                    "DOI": "10.1000/smoke",
                    "extra": "Citation Key: smoke2026",
                    "creators": [{"firstName": "Test", "lastName": "Author"}],
                },
            }
            attachment = {
                "key": "PDF00001",
                "data": {
                    "key": "PDF00001",
                    "itemType": "attachment",
                    "contentType": "application/pdf",
                    "filename": source.name,
                },
            }
            _SmokeHandler.routes = {
                "/api/users/0/items/PAPER001": (200, item),
                "/api/users/0/items/PAPER001/children": (200, [attachment]),
                "/api/users/0/items/PDF00001/file/view/url": (200, source.as_uri()),
            }
            server = ThreadingHTTPServer(("127.0.0.1", 0), _SmokeHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(server.server_close)
            try:
                base = f"http://127.0.0.1:{server.server_port}"
                paper = resolve_item(None, "PAPER001", base)
                pdf = resolve_pdf_attachment(paper, list_children("PAPER001", base), base)
                self.assertEqual(Path(pdf["pdf_path"]).resolve(), source.resolve())
                identity = {
                    **{key: paper.get(key) for key in ("item_key", "title", "doi", "citekey")},
                    "pdf_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                }
                config = {
                    "vault": str(vault),
                    "papers_root": "Research/Papers",
                    "default_language": "both",
                    "note_naming": "slug-language",
                }
                for language, body in (("zh-CN", "# 中文研究资产\n"), ("en", "# Research asset\n")):
                    save_note(
                        preflight(config, identity, language), body, None, config=config
                    )
            finally:
                server.shutdown()
                thread.join(timeout=2)

            notes = list(vault.rglob("*.md"))
            self.assertEqual(len(notes), 2)
            self.assertEqual(list(vault.rglob("*.pdf")), [])
            self.assertTrue(source.exists())


if __name__ == "__main__":
    unittest.main()
