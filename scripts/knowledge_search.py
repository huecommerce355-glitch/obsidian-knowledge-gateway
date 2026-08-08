"""Search markdown and filter indexed metadata."""
import argparse
import json
from pathlib import Path
from knowledge_write import resolve_vault_path, _paths
from knowledge_read import _parse

INDEX_FIELDS = ("path", "title", "type", "project_id", "tags", "status", "date", "trace_id", "review_id", "task_id", "execution_agent", "review_agent", "review_mode", "decision", "score")


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


def _matches_filters(entry, tag=None, status=None, project=None, doc_type=None, agent=None, decision=None, trace_id=None):
    if tag is not None and tag not in entry.get("tags", []):
        return False
    if status is not None and entry.get("status") != status:
        return False
    if project is not None and entry.get("project_id") != project:
        return False
    if doc_type is not None and entry.get("type") != doc_type:
        return False
    if agent is not None and agent not in {entry.get("execution_agent"), entry.get("review_agent")}:
        return False
    if decision is not None and entry.get("decision") != decision:
        return False
    if trace_id is not None and entry.get("trace_id") != trace_id:
        return False
    return True


def search_knowledge(query="", scope="markdown", vault_path=None, project_id=None, tags=None,
                     tag=None, status=None, project=None, doc_type=None, agent=None,
                     decision=None, trace_id=None):
    if scope not in {"markdown", "tags", "project"}: return {"ok": False, "error_code": "ERR-KNG-007", "message": "invalid scope"}
    root = _paths(Path(vault_path) if vault_path else resolve_vault_path())[0]
    # Keep the existing positional API while accepting the v1.1 names.
    selected_tag = tag if tag is not None else (tags[0] if isinstance(tags, (list, tuple)) and len(tags) == 1 else None)
    selected_project = project if project is not None else project_id
    has_filter = any(value is not None for value in (selected_tag, status, selected_project, doc_type, agent, decision, trace_id))
    index = _load_index(root) if has_filter else None
    if isinstance(index, dict) and "error" in index:
        return index["error"]

    candidates = []
    if index is not None:
        candidates = [entry for entry in index.get("documents", [])
                      if isinstance(entry, dict) and _matches_filters(entry, selected_tag, status, selected_project, doc_type, agent, decision, trace_id)]
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
    if doc_type is not None: filtered_by["doc_type"] = doc_type
    if agent is not None: filtered_by["agent"] = agent
    if decision is not None: filtered_by["decision"] = decision
    if trace_id is not None: filtered_by["trace_id"] = trace_id
    return {"ok": True, "results": results, "total": len(results), "filtered_by": filtered_by,
            "documents": documents, "metadata": {"scope": scope, "count": len(documents)}}


def main():
    parser = argparse.ArgumentParser(description="Search the Obsidian knowledge vault")
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--scope", choices=("markdown", "tags", "project"), default="markdown")
    parser.add_argument("--tag")
    parser.add_argument("--status")
    parser.add_argument("--project")
    parser.add_argument("--doc-type")
    parser.add_argument("--agent")
    parser.add_argument("--decision", choices=("PASS", "CONDITIONAL", "FAIL"))
    parser.add_argument("--trace-id")
    parser.add_argument("--vault-path")
    args = parser.parse_args()
    print(json.dumps(search_knowledge(args.query, args.scope, args.vault_path,
                                      tag=args.tag, status=args.status, project=args.project,
                                      doc_type=args.doc_type, agent=args.agent, decision=args.decision,
                                      trace_id=args.trace_id),
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
