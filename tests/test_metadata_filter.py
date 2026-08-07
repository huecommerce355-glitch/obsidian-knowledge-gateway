import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from knowledge_search import search_knowledge
from knowledge_write import write_knowledge


def seed(tmp_path):
    documents = [
        ("Alpha decision", "p1", ["backend", "urgent"], "accepted", "alpha"),
        ("Beta lesson", "p1", ["frontend"], "draft", "beta"),
        ("Gamma report", "p2", ["backend"], "accepted", "gamma"),
    ]
    for title, project, tags, status, body in documents:
        result = write_knowledge("lesson", title, {"body": body}, project_id=project,
                                 tags=tags, status=status, vault_path=tmp_path)
        assert result["ok"], result


def test_metadata_filters_and_combination(tmp_path):
    seed(tmp_path)

    tagged = search_knowledge("", vault_path=tmp_path, tag="backend")
    assert tagged["total"] == 2
    assert {item["project_id"] for item in tagged["results"]} == {"p1", "p2"}
    assert tagged["filtered_by"] == {"tag": "backend"}

    accepted = search_knowledge("", vault_path=tmp_path, status="accepted")
    assert accepted["total"] == 2
    assert all(item["status"] == "accepted" for item in accepted["results"])

    combined = search_knowledge("", vault_path=tmp_path, tag="backend", project="p2")
    assert combined["total"] == 1
    assert combined["results"][0]["title"] == "Gamma report"
    assert combined["filtered_by"] == {"tag": "backend", "project": "p2"}


def test_no_filter_returns_all_and_index_entries_have_status(tmp_path):
    seed(tmp_path)
    result = search_knowledge("", vault_path=tmp_path)
    assert result["total"] == 3
    assert {item["title"] for item in result["results"]} == {"Alpha decision", "Beta lesson", "Gamma report"}
    index = json.loads((tmp_path / "AI-Vault" / ".knowledge-index.yaml").read_text())
    assert all("status" in entry for entry in index["documents"])


def test_adr_and_execution_report_index_entries_have_status(tmp_path):
    for doc_type, title, status, kwargs in [
        ("decision-record", "Index status decision", "accepted", {}),
        ("execution-report", "Index status execution", "completed", {"task_id": "index-status"}),
    ]:
        result = write_knowledge(doc_type, title, {"summary": "status check"}, status=status,
                                 vault_path=tmp_path, **kwargs)
        assert result["ok"], result

    index = json.loads((tmp_path / "AI-Vault" / ".knowledge-index.yaml").read_text())
    entries = {entry["type"]: entry for entry in index["documents"]}
    assert entries["decision-record"]["status"] == "accepted"
    assert entries["execution-report"]["status"] == "completed"
