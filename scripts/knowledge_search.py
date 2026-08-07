"""Search markdown and filter indexed metadata."""
import argparse
import json
from pathlib import Path
from knowledge_write import resolve_vault_path, _paths
from knowledge_read import _parse

INDEX_FIELDS = ("path", "title", "type", "project_id", "tags", "status", "date", "trace_id")


def _load_index(root):
    index_path = root / ".knowledge-index.yaml"
    if not index_path.exists():
        return None
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        if not isinstance(index, dict) or not isinstance(index.get("documents", []), list):
            raise ValueError
    except (OSError, ValueError, json.JSONDecodeError):
        return {"error": {"ok": False, "error_code": "ERR-KNG-006", "message": "knowledge index is damaged"}}
    return index


def _indexed_result(entry):
    return {field: entry.get(field, [] if field == "tags" else "") for field in INDEX_FIELDS}


def _matches_filters(entry, tag=None, status=None, project=None):
    if tag is not None and tag not in entry.get("tags", []):
        return False
    if status is not None and entry.get("status") != status:
        return False
    if project is not None and entry.get("project_id") != project:
        return False
    return True


def search_knowledge(query="", scope="markdown", vault_path=None, project_id=None, tags=None,
                     tag=None, status=None, project=None):
    if scope not in {"markdown", "tags", "project"}: return {"ok": False, "error_code": "ERR-KNG-007", "message": "invalid scope"}
    root = _paths(Path(vault_path) if vault_path else resolve_vault_path())[0]
    # Keep the existing positional API while accepting the v1.1 names.
    selected_tag = tag if tag is not None else (tags[0] if isinstance(tags, (list, tuple)) and len(tags) == 1 else None)
    selected_project = project if project is not None else project_id
    has_filter = selected_tag is not None or status is not None or selected_project is not None
    index = _load_index(root) if has_filter else None
    if isinstance(index, dict) and "error" in index:
        return index["error"]

    candidates = []
    if index is not None:
        candidates = [entry for entry in index.get("documents", [])
                      if isinstance(entry, dict) and _matches_filters(entry, selected_tag, status, selected_project)]
    else:
        candidates = [{"_path": path} for path in (root.rglob("*.md") if root.exists() else [])]

    documents = []
    results = []
    for candidate in candidates:
        path = root / candidate["path"] if "path" in candidate else candidate["_path"]
        if not path.is_file():
            continue
        meta, body = _parse(path)
        haystack = body + " " + json.dumps(meta, ensure_ascii=False)
        if scope == "markdown" and query.lower() not in haystack.lower(): continue
        if scope == "tags" and query not in meta.get("tags", []): continue
        if scope == "project" and (project_id or query) != meta.get("project_id"): continue
        entry = candidate if "path" in candidate else {
            "path": str(path.relative_to(root)), **meta
        }
        result = _indexed_result(entry)
        # The legacy response remains available to M0.1 callers.
        documents.append({"path": str(path), "frontmatter": meta, "summary": body[:500]})
        results.append(result)
    filtered_by = {}
    if selected_tag is not None: filtered_by["tag"] = selected_tag
    if status is not None: filtered_by["status"] = status
    if selected_project is not None: filtered_by["project"] = selected_project
    return {"ok": True, "results": results, "total": len(results), "filtered_by": filtered_by,
            "documents": documents, "metadata": {"scope": scope, "count": len(documents)}}


def main():
    parser = argparse.ArgumentParser(description="Search the Obsidian knowledge vault")
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--scope", choices=("markdown", "tags", "project"), default="markdown")
    parser.add_argument("--tag")
    parser.add_argument("--status")
    parser.add_argument("--project")
    parser.add_argument("--vault-path")
    args = parser.parse_args()
    print(json.dumps(search_knowledge(args.query, args.scope, args.vault_path,
                                      tag=args.tag, status=args.status, project=args.project),
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
