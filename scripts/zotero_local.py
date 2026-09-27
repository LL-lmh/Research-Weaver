#!/usr/bin/env python3
"""Read papers and attachments from Zotero Desktop's local read-only API."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import PureWindowsPath
from typing import Any


DEFAULT_BASE_URL = "http://127.0.0.1:23119"
LOCAL_USER = "/api/users/0"
API_HEADERS = {"Zotero-API-Version": "3", "Accept": "application/json"}


class ZoteroError(RuntimeError):
    """Base error for Zotero Local API operations."""


class ZoteroConnectionError(ZoteroError):
    """Raised when Zotero Desktop's local API cannot be reached."""


class ZoteroAPIError(ZoteroError):
    """Raised when the local API returns an unsuccessful response."""


class ZoteroNotFoundError(ZoteroError):
    """Raised when no paper or PDF attachment matches."""


class ZoteroAmbiguousError(ZoteroError):
    """Raised when a query resolves to more than one plausible paper."""

    def __init__(self, candidates: list[str]):
        self.candidates = candidates
        super().__init__(f"Ambiguous Zotero paper: {', '.join(candidates)}")


def api_get(path: str, base_url: str = DEFAULT_BASE_URL) -> Any:
    url = base_url.rstrip("/") + (path if path.startswith("/") else "/" + path)
    request = urllib.request.Request(url, headers=API_HEADERS, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            raw = response.read().decode("utf-8", errors="replace")
            content_type = response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ZoteroAPIError(f"GET {path} failed with HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ZoteroConnectionError(
            f"Cannot reach Zotero Local API at {base_url}. Start Zotero and enable its local API."
        ) from exc
    if "json" in content_type.lower():
        return json.loads(raw or "null")
    return raw


def _creator_names(data: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for creator in data.get("creators") or []:
        name = creator.get("name") or " ".join(
            value for value in (creator.get("firstName"), creator.get("lastName")) if value
        )
        if name:
            names.append(name)
    return names


def _year(value: str | None) -> str | None:
    match = re.search(r"\b(\d{4})\b", value or "")
    return match.group(1) if match else None


def _citekey(data: dict[str, Any]) -> str | None:
    if data.get("citationKey"):
        return str(data["citationKey"])
    match = re.search(r"(?im)^Citation Key:\s*(\S+)\s*$", data.get("extra") or "")
    return match.group(1) if match else None


def _arxiv_id(data: dict[str, Any]) -> str | None:
    for value in (data.get("archiveLocation"), data.get("extra"), data.get("url")):
        match = re.search(r"(?i)(?:arXiv[:/\s]+)(\d{4}\.\d{4,5}(?:v\d+)?)", value or "")
        if match:
            return match.group(1)
    return None


def _query_identifier(query: str) -> tuple[str | None, str | None]:
    doi_match = re.search(r"(?i)(?:https?://(?:dx\.)?doi\.org/|doi:\s*)?(10\.\d{4,9}/\S+)", query)
    if doi_match:
        return "doi", doi_match.group(1).rstrip(".,;)").lower()
    arxiv_match = re.search(r"(?i)(?:arxiv:\s*|arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5}(?:v\d+)?)", query)
    if arxiv_match:
        return "arxiv", arxiv_match.group(1).lower()
    return None, None


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    data = item.get("data", item)
    return {
        "item_key": item.get("key") or data.get("key"),
        "item_type": data.get("itemType"),
        "title": data.get("title"),
        "authors": _creator_names(data),
        "year": _year(data.get("date")),
        "doi": data.get("DOI") or None,
        "arxiv_id": _arxiv_id(data),
        "citekey": _citekey(data),
    }


def search_items(query: str, base_url: str = DEFAULT_BASE_URL) -> list[dict[str, Any]]:
    encoded = urllib.parse.urlencode({"q": query, "qmode": "everything"})
    rows = api_get(f"{LOCAL_USER}/items/top?{encoded}", base_url)
    if not isinstance(rows, list):
        raise ZoteroAPIError("Zotero search returned a non-list response")
    matches = [normalize_item(row) for row in rows]
    kind, identifier = _query_identifier(query)
    if kind == "doi":
        matches = [row for row in matches if str(row.get("doi") or "").lower() == identifier]
    elif kind == "arxiv":
        matches = [row for row in matches if str(row.get("arxiv_id") or "").lower() == identifier]
    return matches


def resolve_item(
    query: str | None,
    item_key: str | None,
    base_url: str = DEFAULT_BASE_URL,
) -> dict[str, Any]:
    if item_key:
        encoded = urllib.parse.quote(item_key, safe="")
        item = api_get(f"{LOCAL_USER}/items/{encoded}", base_url)
        if not isinstance(item, dict):
            raise ZoteroAPIError("Zotero item response was not an object")
        return normalize_item(item)
    if not query:
        raise ValueError("Provide query or item_key")
    matches = search_items(query, base_url)
    if not matches:
        raise ZoteroNotFoundError(f"No Zotero paper matched: {query}")
    if len(matches) != 1:
        raise ZoteroAmbiguousError([str(row.get("item_key") or "") for row in matches])
    return matches[0]


def list_children(item_key: str, base_url: str = DEFAULT_BASE_URL) -> list[dict[str, Any]]:
    encoded = urllib.parse.quote(item_key, safe="")
    rows = api_get(f"{LOCAL_USER}/items/{encoded}/children", base_url)
    if not isinstance(rows, list):
        raise ZoteroAPIError("Zotero children response was not a list")
    return rows


def _file_url_to_path(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("url") or value.get("fileURL") or value.get("path")
    if not isinstance(value, str) or not value:
        raise ZoteroAPIError("Zotero attachment did not return a file URL")
    parsed = urllib.parse.urlparse(value)
    decoded = urllib.parse.unquote(parsed.path if parsed.scheme == "file" else value)
    if parsed.scheme == "file" and parsed.netloc and parsed.netloc.lower() != "localhost":
        return str(PureWindowsPath(f"//{parsed.netloc}{decoded}"))
    if re.match(r"^/[A-Za-z]:/", decoded):
        decoded = decoded[1:]
    if re.match(r"^[A-Za-z]:/", decoded):
        return str(PureWindowsPath(decoded))
    return decoded


def resolve_pdf_attachment(
    item: dict[str, Any],
    children: list[dict[str, Any]],
    base_url: str = DEFAULT_BASE_URL,
) -> dict[str, Any]:
    pdfs = []
    for child in children:
        data = child.get("data", child)
        if data.get("itemType") == "attachment" and (
            data.get("contentType") == "application/pdf"
            or str(data.get("filename") or "").lower().endswith(".pdf")
        ):
            pdfs.append(child)
    if not pdfs:
        raise ZoteroNotFoundError(f"No PDF attachment for {item.get('item_key')}")
    if len(pdfs) > 1:
        preferred = [row for row in pdfs if (row.get("data", row)).get("linkMode") != "linked_url"]
        pdfs = preferred or pdfs
    if len(pdfs) != 1:
        raise ZoteroAmbiguousError(
            [str(row.get("key") or row.get("data", {}).get("key") or "") for row in pdfs]
        )
    attachment = pdfs[0]
    data = attachment.get("data", attachment)
    key = attachment.get("key") or data.get("key")
    file_value = api_get(
        f"{LOCAL_USER}/items/{urllib.parse.quote(str(key), safe='')}/file/view/url",
        base_url,
    )
    return {
        "attachment_key": key,
        "filename": data.get("filename"),
        "pdf_path": _file_url_to_path(file_value),
    }


def fulltext(attachment_key: str, base_url: str = DEFAULT_BASE_URL) -> dict[str, Any]:
    encoded = urllib.parse.quote(attachment_key, safe="")
    value = api_get(f"{LOCAL_USER}/items/{encoded}/fulltext", base_url)
    if not isinstance(value, dict):
        raise ZoteroAPIError("Zotero full-text response was not an object")
    return value


def _print(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    search = sub.add_parser("search")
    search.add_argument("query")
    resolve = sub.add_parser("resolve")
    group = resolve.add_mutually_exclusive_group(required=True)
    group.add_argument("--query")
    group.add_argument("--item-key")
    children = sub.add_parser("children")
    children.add_argument("item_key")
    full = sub.add_parser("fulltext")
    full.add_argument("attachment_key")
    file_url = sub.add_parser("file-url")
    file_url.add_argument("attachment_key")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        if args.command == "status":
            _print({"api_running": isinstance(api_get("/api/", args.base_url), (dict, list, str))})
        elif args.command == "search":
            _print(search_items(args.query, args.base_url))
        elif args.command == "resolve":
            paper = resolve_item(args.query, args.item_key, args.base_url)
            paper["attachment"] = resolve_pdf_attachment(
                paper, list_children(paper["item_key"], args.base_url), args.base_url
            )
            _print(paper)
        elif args.command == "children":
            _print(list_children(args.item_key, args.base_url))
        elif args.command == "fulltext":
            _print(fulltext(args.attachment_key, args.base_url))
        elif args.command == "file-url":
            value = api_get(
                f"{LOCAL_USER}/items/{urllib.parse.quote(args.attachment_key, safe='')}/file/view/url",
                args.base_url,
            )
            _print({"pdf_path": _file_url_to_path(value)})
        return 0
    except (ZoteroError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
