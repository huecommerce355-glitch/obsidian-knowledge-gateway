import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from knowledge_write import write_knowledge

def test_six_document_types_and_frontmatter(tmp_path):
    cases = [("execution-report", "task"), ("agent-result", "agent"), ("test-result", "suite"), ("decision-record", "Use cache"), ("project-context", "project"), ("lesson", "Testing")]
    for kind, title in cases:
        content = {"summary": "ok", "metrics": {"passed": 1}, "artifacts": ["reports/a.txt"], "body": "details"}
        result = write_knowledge(kind, title, content, project_id="p1", vault_path=tmp_path, agent_id="a1", task_id="t1", suite="s1")
        assert result["ok"], result
    files = list((tmp_path / "AI-Vault").rglob("*.md"))
    assert len(files) == 6
    report = next(p for p in files if "Execution-Reports" in str(p) and "/tests/" not in str(p))
    text = report.read_text()
    assert "created_by" in text and "details" not in text

def test_write_safety_and_no_overwrite(tmp_path):
    first = write_knowledge("lesson", "one", "safe", vault_path=tmp_path)
    assert first["ok"]
    second = write_knowledge("lesson", "one", "changed", vault_path=tmp_path)
    assert second["error_code"] == "ERR-KNG-007"
    blocked = write_knowledge("lesson", "bad", "token=secret", vault_path=tmp_path)
    assert blocked["error_code"] == "ERR-KNG-004"

