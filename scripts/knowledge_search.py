"""Search frontmatter and markdown content."""
import json
from pathlib import Path
from knowledge_write import resolve_vault_path, _paths
from knowledge_read import _parse

def search_knowledge(query, scope="markdown", vault_path=None, project_id=None, tags=None):
    if scope not in {"markdown", "tags", "project"}: return {"ok": False, "error_code": "ERR-KNG-007", "message": "invalid scope"}
    root = _paths(Path(vault_path) if vault_path else resolve_vault_path())[0]
    results = []
    for path in root.rglob("*.md") if root.exists() else []:
        meta, body = _parse(path); haystack = body + " " + json.dumps(meta, ensure_ascii=False)
        if scope == "markdown" and query.lower() not in haystack.lower(): continue
        if scope == "tags" and query not in meta.get("tags", []): continue
        if scope == "project" and (project_id or query) != meta.get("project_id"): continue
        results.append({"path": str(path), "frontmatter": meta, "summary": body[:500]})
    return {"ok": True, "documents": results, "metadata": {"scope": scope, "count": len(results)}}
