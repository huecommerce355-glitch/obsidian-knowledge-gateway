import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from knowledge_write import write_knowledge


def test_adr_index_update_after_decision_record_write(tmp_path):
    result = write_knowledge(
        doc_type="decision-record",
        title="Choose cache strategy",
        content={"summary": "Use the shared cache."},
        project_id="project-1",
        status="accepted",
        vault_path=tmp_path,
    )

    assert result["ok"], result
    index_path = tmp_path / "AI-Vault" / ".knowledge-index.yaml"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = index["documents"][0]
    assert entry["path"].startswith("Decisions/ADR-001-")
    assert entry["path"].endswith(".md")
    assert entry["type"] == "decision-record"
    assert entry["status"] == "accepted"
    datetime.fromisoformat(index["last_indexed"])


def test_adr_numbering_compatibility(tmp_path):
    decisions = tmp_path / "AI-Vault" / "Decisions"
    decisions.mkdir(parents=True)
    legacy = decisions / "ADR-1-legacy.md"
    legacy.write_text("# Legacy ADR\n", encoding="utf-8")

    result = write_knowledge(
        doc_type="decision-record",
        title="New decision",
        content={"summary": "Keep the legacy record."},
        vault_path=tmp_path,
    )

    assert result["ok"], result
    assert legacy.exists()
    assert (decisions / "ADR-002-new-decision.md").exists()


def test_ai_vault_root_consistency(tmp_path):
    result = write_knowledge(
        doc_type="decision-record",
        title="Root consistency",
        content={"summary": "Use the AI-Vault root."},
        vault_path=tmp_path,
    )

    assert result["ok"], result
    root = tmp_path / "AI-Vault"
    document_path = Path(result["document"]["path"])
    assert document_path.is_relative_to(root)
    assert document_path.parent == root / "Decisions"
    assert not (tmp_path / "Decisions").exists()
