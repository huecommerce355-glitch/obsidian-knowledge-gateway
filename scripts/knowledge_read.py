"""Read knowledge documents without exposing full bodies by default."""
import json, re
from pathlib import Path
from knowledge_write import resolve_vault_path, _paths, DOC_TYPES

def _parse(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"): return {}, text
    end = text.find("\n---", 4)
    if end < 0: return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1); value = value.strip()
            try: meta[key] = json.loads(value)
            except json.JSONDecodeError: meta[key] = value
    return meta, text[end + 4:].lstrip("\n")

def read_knowledge(doc_type, doc_id, vault_path=None, full=False, project_id="", **kwargs):
    if doc_type not in DOC_TYPES: return {"ok": False, "error_code": "ERR-KNG-002", "message": "invalid doc_type"}
    root, dirs = _paths(Path(vault_path) if vault_path else resolve_vault_path())
    candidates = list(root.rglob("*.md")) if root.exists() else []
    for path in candidates:
        meta, body = _parse(path)
        if meta.get("type") == doc_type and (doc_id in {path.stem, meta.get("title"), str(path), meta.get("id")}):
            doc = {"path": str(path), "frontmatter": meta, "summary": body[:500]}
            if full: doc["body"] = body
            return {"ok": True, "document": doc}
    return {"ok": False, "error_code": "ERR-KNG-005", "message": "document not found"}
