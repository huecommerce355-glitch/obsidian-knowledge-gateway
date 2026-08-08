import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from knowledge_read import read_knowledge
from knowledge_search import search_knowledge
from knowledge_write import write_knowledge


def review(tmp_path, decision="PASS", task_id="task-1"):
    return write_knowledge(
        "review-result", "Review " + task_id,
        {"summary": "safe summary", "scores": {"quality": 9},
         "findings": ["All checks passed"], "blockers": ["release blocker summary"],
         "body": "raw diff and complete agent output must not be persisted"},
        project_id="p1", vault_path=tmp_path, trace_id="trace-1", review_id="review-1",
        task_id=task_id, execution_agent="executor", review_agent="reviewer",
        review_mode="standard", decision=decision, score=9,
    )


def test_review_pass_writes_frontmatter_and_index(tmp_path):
    result = review(tmp_path)
    assert result["ok"], result
    path = Path(result["document"]["path"])
    assert path.parent == tmp_path / "AI-Vault" / "Reviews"
    meta = result["document"]["frontmatter"]
    fields = ("review_id", "task_id", "trace_id", "execution_agent", "review_agent", "review_mode", "decision", "score")
    assert all(field in meta for field in fields)
    body = path.read_text(encoding="utf-8")
    assert "raw diff and complete agent output" not in body and "## Summary" in body
    entry = json.loads((tmp_path / "AI-Vault" / ".knowledge-index.yaml").read_text())["documents"][0]
    assert all(field in entry for field in fields)


def test_review_fail_preserves_blocker_summary(tmp_path):
    result = review(tmp_path, decision="FAIL", task_id="task-fail")
    assert result["ok"], result
    body = Path(result["document"]["path"]).read_text(encoding="utf-8")
    assert 'decision: "FAIL"' in body
    assert "release blocker summary" in body


def test_trace_id_search_associates_review(tmp_path):
    review(tmp_path)
    result = search_knowledge("", vault_path=tmp_path, doc_type="review-result", trace_id="trace-1")
    assert result["total"] == 1
    assert result["results"][0]["review_id"] == "review-1"


def test_legacy_documents_and_index_without_review_fields_remain_readable(tmp_path):
    root = tmp_path / "AI-Vault" / "Knowledge"
    root.mkdir(parents=True)
    (root / "legacy.md").write_text(
        '---\ntitle: "Legacy"\ntype: "lesson"\nproject_id: "p1"\n'
        'date: "2026-01-01"\nstatus: "active"\ntags: []\n---\n\nlegacy body\n', encoding="utf-8")
    (tmp_path / "AI-Vault" / ".knowledge-index.yaml").write_text(json.dumps({"documents": [{
        "path": "Knowledge/legacy.md", "title": "Legacy", "type": "lesson", "project_id": "p1",
        "status": "active", "tags": [], "date": "2026-01-01"
    }]}), encoding="utf-8")
    assert read_knowledge("lesson", "legacy", vault_path=tmp_path)["ok"]
    result = search_knowledge("legacy body", vault_path=tmp_path)
    assert result["ok"] and result["total"] == 1
