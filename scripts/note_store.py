#!/usr/bin/env python3
"""Safely admit and atomically save Research Weaver notes in an Obsidian vault."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any


SUPPORTED_LANGUAGES = {"zh-CN", "en"}
SIDECAR_NAME = ".research-weaver.json"
IDENTITY_FIELDS = ("item_key", "title", "doi", "citekey", "pdf_sha256")
CONFIG_ENV = "RESEARCH_WEAVER_CONFIG"


class NoteStoreError(RuntimeError):
    """Base error for safe note storage."""


class IdentityConflictError(NoteStoreError):
    """A target directory belongs to a different paper."""


class OverwriteDeniedError(NoteStoreError):
    """An existing note was not authorized for its current exact content."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slug(value: str, fallback: str = "paper") -> str:
    value = unicodedata.normalize("NFKC", value).strip()
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip(" .-")
    return value[:100] or fallback


def _identity(raw: dict[str, Any]) -> dict[str, str]:
    identity = {field: str(raw.get(field) or "").strip() for field in IDENTITY_FIELDS}
    if not identity["item_key"] or not identity["title"]:
        raise ValueError("identity requires item_key and title")
    return identity


def _same_identity(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_id, right_id = _identity(left), _identity(right)
    if left_id["item_key"] != right_id["item_key"]:
        return False
    for field in ("doi", "citekey", "pdf_sha256"):
        if left_id[field] and right_id[field] and left_id[field] != right_id[field]:
            return False
    return True


def default_config_path() -> Path:
    """Return the private per-user configuration path without creating it."""
    override = os.environ.get(CONFIG_ENV)
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return (base / "research-weaver" / "config.json").resolve()


def _validate_config(config: dict[str, Any]) -> dict[str, Any]:
    required = {"vault", "papers_root", "default_language", "note_naming"}
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"configuration missing: {', '.join(missing)}")
    vault = Path(config["vault"])
    if not vault.is_absolute() or not vault.is_dir():
        raise ValueError("vault must be an existing absolute directory")
    root = Path(config["papers_root"])
    if root.is_absolute() or ".." in root.parts:
        raise ValueError("papers_root must stay inside the vault")
    if config["default_language"] not in SUPPORTED_LANGUAGES | {"both"}:
        raise ValueError("default_language must be zh-CN, en, or both")
    if config["note_naming"] != "slug-language":
        raise ValueError("note_naming must be slug-language")
    return {**config, "vault": str(vault.resolve())}


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load and validate a runtime configuration file."""
    target = Path(path) if path is not None else default_config_path()
    config = json.loads(target.read_text(encoding="utf-8"))
    return _validate_config(config)


def save_config(config: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    """Validate and atomically save a private per-user configuration."""
    validated = _validate_config(config)
    target = (Path(path) if path is not None else default_config_path()).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(validated, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = _write_temp(target.parent, payload)
    try:
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    try:
        target.chmod(0o600)
    except OSError:
        pass
    return {"config_path": str(target), "config": validated}


def _read_sidecar(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise NoteStoreError(f"cannot read identity sidecar: {path}") from exc


def _find_identity_dir(root: Path, identity: dict[str, str]) -> Path | None:
    if not root.exists():
        return None
    for sidecar in root.glob(f"*/{SIDECAR_NAME}"):
        stored = _read_sidecar(sidecar).get("identity", {})
        if _same_identity(stored, identity):
            return sidecar.parent
    return None


def _paper_directory_name(identity: dict[str, str]) -> str:
    anchor = identity["citekey"] or identity["item_key"]
    return _slug(f"{identity['title']}--{anchor}")


def preflight(config: dict[str, Any], identity: dict[str, Any], language: str) -> dict[str, Any]:
    """Resolve a note target without overwriting any content."""
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError("language must be zh-CN or en; expand 'both' before preflight")
    normalized = _identity(identity)
    vault = Path(config["vault"])
    if not vault.is_absolute() or not vault.is_dir():
        raise ValueError("vault must be an existing absolute directory")
    papers_root = (vault / config["papers_root"]).resolve()
    try:
        papers_root.relative_to(vault.resolve())
    except ValueError as exc:
        raise ValueError("papers_root must stay inside the vault") from exc
    papers_root.mkdir(parents=True, exist_ok=True)

    paper_dir = _find_identity_dir(papers_root, normalized)
    candidate = papers_root / _paper_directory_name(normalized)
    if paper_dir is None:
        paper_dir = candidate
        sidecar = paper_dir / SIDECAR_NAME
        if sidecar.exists() and not _same_identity(_read_sidecar(sidecar).get("identity", {}), normalized):
            raise IdentityConflictError(f"paper directory belongs to another identity: {paper_dir}")
        paper_dir.mkdir(parents=True, exist_ok=True)
    elif paper_dir != candidate and candidate.exists():
        candidate_sidecar = candidate / SIDECAR_NAME
        if candidate_sidecar.exists() and not _same_identity(
            _read_sidecar(candidate_sidecar).get("identity", {}), normalized
        ):
            raise IdentityConflictError(f"paper directory collision: {candidate}")

    # Detect the common collision even before a sidecar scan can match it.
    sidecar_path = paper_dir / SIDECAR_NAME
    sidecar_data: dict[str, Any] | None = None
    if sidecar_path.exists():
        sidecar_data = _read_sidecar(sidecar_path)
        stored = sidecar_data.get("identity", {})
        if not _same_identity(stored, normalized):
            raise IdentityConflictError(f"paper identity conflict: {paper_dir}")

    stored_variant = (sidecar_data or {}).get("variants", {}).get(language, {})
    filename = str(stored_variant.get("file") or f"{_slug(normalized['title'])}.{language}.md")
    if Path(filename).name != filename:
        raise IdentityConflictError("sidecar variant path must be a filename")
    note_path = paper_dir / filename
    existing_sha = _sha256(note_path.read_bytes()) if note_path.exists() else None
    return {
        "status": "existing" if note_path.exists() else "new",
        "paper_dir": str(paper_dir),
        "note_path": str(note_path),
        "existing_sha256": existing_sha,
        "identity": normalized,
        "language": language,
    }


def _write_temp(directory: Path, payload: bytes) -> Path:
    handle = tempfile.NamedTemporaryFile(
        mode="wb", prefix=".research-weaver-", suffix=".tmp", dir=directory, delete=False
    )
    path = Path(handle.name)
    try:
        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        return path
    except Exception:
        path.unlink(missing_ok=True)
        raise


def save_note(
    preflight_result: dict[str, Any],
    markdown: str,
    expected_existing_sha256: str | None,
    *,
    config: dict[str, Any],
) -> dict[str, str]:
    """Atomically create or hash-authorized update a note and its identity sidecar."""
    fresh = preflight(
        config,
        preflight_result["identity"],
        preflight_result["language"],
    )
    for field in ("paper_dir", "note_path"):
        if Path(fresh[field]).resolve() != Path(preflight_result[field]).resolve():
            raise IdentityConflictError(f"stale or tampered preflight {field}")
    preflight_result = fresh
    note_path = Path(fresh["note_path"])
    paper_dir = Path(fresh["paper_dir"])
    paper_dir.mkdir(parents=True, exist_ok=True)
    sidecar_path = paper_dir / SIDECAR_NAME
    existed = note_path.exists()
    current_bytes = note_path.read_bytes() if existed else None
    current_sha = _sha256(current_bytes) if current_bytes is not None else None
    if existed and (not expected_existing_sha256 or expected_existing_sha256 != current_sha):
        raise OverwriteDeniedError("existing note requires its current SHA-256 for overwrite")
    if not existed and expected_existing_sha256 is not None:
        raise OverwriteDeniedError("new note must not provide an overwrite hash")

    identity = _identity(preflight_result["identity"])
    if sidecar_path.exists():
        sidecar = _read_sidecar(sidecar_path)
        if not _same_identity(sidecar.get("identity", {}), identity):
            raise IdentityConflictError(f"paper identity conflict: {paper_dir}")
    else:
        sidecar = {"schema_version": 1, "identity": identity, "variants": {}}
    sidecar["identity"] = identity

    note_bytes = markdown.encode("utf-8")
    note_sha = _sha256(note_bytes)
    sidecar["variants"][preflight_result["language"]] = {
        "file": note_path.name,
        "sha256": note_sha,
    }
    sidecar_bytes = (json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    note_temp = _write_temp(paper_dir, note_bytes)
    sidecar_temp = _write_temp(paper_dir, sidecar_bytes)
    old_sidecar = sidecar_path.read_bytes() if sidecar_path.exists() else None
    sidecar_replaced = False
    try:
        os.replace(sidecar_temp, sidecar_path)
        sidecar_replaced = True
        # Commit the note last. An interruption before this atomic replace leaves
        # the previous note intact; a completed replace makes the new pair usable.
        os.replace(note_temp, note_path)
    except Exception:
        if sidecar_replaced:
            if old_sidecar is None:
                sidecar_path.unlink(missing_ok=True)
            else:
                rollback_temp = _write_temp(paper_dir, old_sidecar)
                try:
                    os.replace(rollback_temp, sidecar_path)
                finally:
                    rollback_temp.unlink(missing_ok=True)
        raise
    finally:
        note_temp.unlink(missing_ok=True)
        sidecar_temp.unlink(missing_ok=True)

    return {
        "note_path": str(note_path),
        "note_sha256": note_sha,
        "action": "updated" if existed else "created",
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    configure = sub.add_parser("configure", help="save first-run private configuration")
    configure.add_argument("--config", type=Path)
    configure.add_argument("--vault", required=True)
    configure.add_argument("--papers-root", required=True)
    configure.add_argument(
        "--default-language", choices=["zh-CN", "en", "both"], required=True
    )
    configure.add_argument("--index-note", default="")
    show = sub.add_parser("show-config", help="show the resolved saved configuration")
    show.add_argument("--config", type=Path)
    check = sub.add_parser("preflight", help="resolve a safe note destination")
    check.add_argument("--config", required=True, type=Path)
    check.add_argument("--identity", required=True, type=Path, help="JSON identity file")
    check.add_argument("--language", choices=sorted(SUPPORTED_LANGUAGES), required=True)
    save = sub.add_parser("save", help="atomically save Markdown after preflight")
    save.add_argument("--config", required=True, type=Path)
    save.add_argument("--preflight", required=True, type=Path, help="preflight JSON file")
    save.add_argument("--markdown", required=True, type=Path)
    save.add_argument("--expected-existing-sha256")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = _build_parser().parse_args(argv)
    if args.command == "configure":
        result = save_config(
            {
                "vault": args.vault,
                "papers_root": args.papers_root,
                "default_language": args.default_language,
                "note_naming": "slug-language",
                "index_note": args.index_note,
            },
            args.config,
        )
    elif args.command == "show-config":
        target = args.config or default_config_path()
        result = {"config_path": str(Path(target).resolve()), "config": load_config(target)}
    elif args.command == "preflight":
        config = load_config(args.config)
        identity = json.loads(args.identity.read_text(encoding="utf-8"))
        result = preflight(config, identity, args.language)
    else:
        config = load_config(args.config)
        admission = json.loads(args.preflight.read_text(encoding="utf-8"))
        markdown = args.markdown.read_text(encoding="utf-8")
        result = save_note(
            admission,
            markdown,
            args.expected_existing_sha256,
            config=config,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
