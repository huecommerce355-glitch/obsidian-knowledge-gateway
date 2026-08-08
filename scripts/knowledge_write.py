"""Safe HACP knowledge writer for the Obsidian Knowledge Gateway."""
import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path

DOC_TYPES = {"execution-report", "agent-result", "test-result", "decision-record", "project-context", "lesson", "review-result"}
REVIEW_FIELDS = ("review_id", "task_id", "trace_id", "execution_agent", "review_agent", "review_mode", "decision", "score")
ERRORS = {"vault": "ERR-KNG-001", "doc_type": "ERR-KNG-002", "required": "ERR-KNG-003", "safety": "ERR-KNG-004", "not_found": "ERR-KNG-005", "index": "ERR-KNG-006", "input": "ERR-KNG-007"}

def resolve_vault_path():
    configured = os.environ.get("OBSIDIAN_VAULT_PATH")
    if configured and Path(configured).is_dir():
        return Path(configured).expanduser().resolve()
    return Path.home() / "Documents" / "Obsidian Vault"

def _safe_slug(value):
    return re.sub(r"[^a-z0-9-]+", "-", str(value).lower()).strip("-") or "untitled"

def _paths(vault):
    root = Path(vault) / "AI-Vault"
    return root, {
        "project-context": root / "Projects",
        "agent-result": root / "Agents",
        "decision-record": root / "Decisions",
        "execution-report": root / "Execution-Reports",
        "test-result": root / "Execution-Reports" / "tests",
        "lesson": root / "Knowledge",
        "review-result": root / "Reviews",
    }

def _frontmatter(meta):
    lines = ["---"]
    keys = ("title", "type", "project_id", "date", "status", "tags", "created_by")
    if meta.get("type") == "review-result":
        keys += REVIEW_FIELDS
    elif meta.get("trace_id"):
        keys += ("trace_id",)
    for key in keys:
        value = meta.get(key, [] if key == "tags" else "")
        if isinstance(value, list):
            lines.append(key + ": [" + ", ".join(json.dumps(str(x), ensure_ascii=False) for x in value) + "]")
        else:
            lines.append(key + ": " + json.dumps(str(value), ensure_ascii=False))
    lines += ["---", ""]
    return "\n".join(lines)

def _body(doc_type, content):
    content = content or {}
    if not isinstance(content, dict):
        content = {"summary": ""} if doc_type in {"execution-report", "test-result"} else {"summary": str(content)}
    if doc_type in {"execution-report", "test-result"}:
        summary, metrics, artifacts = content.get("summary", ""), content.get("metrics", {}), content.get("artifacts", [])
        return "## Summary\n" + str(summary) + "\n\n## Metrics\n" + json.dumps(metrics, ensure_ascii=False, indent=2) + "\n\n## Artifacts\n" + "\n".join("- " + str(x) for x in artifacts) + "\n"
    if doc_type == "review-result":
        sections = []
        for heading, key in (("Summary", "summary"), ("Scores", "scores"), ("Findings", "findings"), ("Blockers", "blockers")):
            if key not in content or content[key] in (None, "", [], {}):
                continue
            value = content[key]
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False, indent=2)
            sections.append("## " + heading + "\n" + value[:4000].rstrip())
        return "\n\n".join(sections) + "\n"
    if "body" in content:
        return str(content["body"]).rstrip() + "\n"
    return "## Summary\n" + str(content.get("summary", "")) + "\n"

def _next_adr(directory):
    numbers = [int(m.group(1)) for p in directory.glob("ADR-*.md") if (m := re.match(r"ADR-(\d+)-", p.name))]
    return max(numbers, default=0) + 1

def _update_index(root, entry):
    path = root / ".knowledge-index.yaml"
    data = {"last_indexed": None, "documents": []}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict) or not isinstance(loaded.get("documents", []), list): raise ValueError
            data.update(loaded)
        except (ValueError, json.JSONDecodeError):
            return {"ok": False, "error_code": ERRORS["index"], "message": "knowledge index is damaged"}
    data["documents"] = [x for x in data["documents"] if x.get("path") != entry["path"]]
    data["documents"].append(entry)
    data["last_indexed"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)
    return {"ok": True}

def write_knowledge(doc_type, title, content, project_id="", status="active", tags=None, vault_path=None, overwrite=False, trace_id=None, **kwargs):
    if doc_type not in DOC_TYPES: return {"ok": False, "error_code": ERRORS["doc_type"], "message": "invalid doc_type"}
    if not title or content is None: return {"ok": False, "error_code": ERRORS["required"], "message": "title and content are required"}
    if doc_type == "review-result":
        review_values = {field: trace_id if field == "trace_id" else kwargs.get(field) for field in REVIEW_FIELDS}
        missing = [field for field, value in review_values.items() if value in (None, "")]
        if missing:
            return {"ok": False, "error_code": ERRORS["required"], "message": "review fields are required: " + ", ".join(missing)}
        if review_values["decision"] not in {"PASS", "CONDITIONAL", "FAIL"}:
            return {"ok": False, "error_code": ERRORS["input"], "message": "invalid review decision"}
    from safety_filter import check
    safety = check(content)
    if not safety["ok"]: return safety
    vault = Path(vault_path) if vault_path else resolve_vault_path()
    if not vault.is_dir(): return {"ok": False, "error_code": ERRORS["vault"], "message": "vault is unavailable"}
    root, dirs = _paths(vault)
    today = date.today().isoformat()
    if doc_type == "project-context": directory, filename = dirs[doc_type] / _safe_slug(project_id or title), "context.md"
    elif doc_type == "agent-result": directory, filename = dirs[doc_type] / _safe_slug(kwargs.get("agent_id", project_id or "default")) / "results", today + "-" + _safe_slug(title) + ".md"
    elif doc_type == "decision-record":
        directory, filename = dirs[doc_type], "ADR-%03d-%s.md" % (_next_adr(dirs[doc_type]), _safe_slug(title))
    elif doc_type == "execution-report": directory, filename = dirs[doc_type], today + "-" + _safe_slug(kwargs.get("task_id", title)) + ".md"
    elif doc_type == "test-result": directory, filename = dirs[doc_type], today + "-" + _safe_slug(kwargs.get("suite", title)) + ".md"
    elif doc_type == "review-result": directory, filename = dirs[doc_type], today + "-" + _safe_slug(kwargs["task_id"]) + "-review.md"
    else: directory, filename = dirs[doc_type], _safe_slug(title) + ".md"
    path = directory / filename
    if path.exists() and not overwrite: return {"ok": False, "error_code": ERRORS["input"], "message": "refusing to overwrite existing document", "path": str(path)}
    directory.mkdir(parents=True, exist_ok=True)
    os.chmod(directory, 0o750)
    meta = {"title": title, "type": doc_type, "project_id": project_id, "date": today, "status": status, "tags": tags or [], "created_by": "obsidian-knowledge-gateway"}
    if doc_type == "review-result":
        meta.update({field: (trace_id if field == "trace_id" else kwargs[field]) for field in REVIEW_FIELDS})
    elif trace_id:
        meta["trace_id"] = trace_id
    path.write_text(_frontmatter(meta) + _body(doc_type, content), encoding="utf-8")
    os.chmod(path, 0o640)
    entry = {"path": str(path.relative_to(root)), "title": title, "type": doc_type, "project_id": project_id, "status": status, "tags": tags or [], "date": today}
    if trace_id:
        entry["trace_id"] = trace_id
    if doc_type == "review-result":
        entry.update({field: meta[field] for field in REVIEW_FIELDS})
    indexed = _update_index(root, entry)
    if not indexed["ok"]: return indexed
    return {"ok": True, "document": {"path": str(path), "frontmatter": meta}}
