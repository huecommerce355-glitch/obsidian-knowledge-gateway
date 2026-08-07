import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from knowledge_read import read_knowledge
from knowledge_search import search_knowledge
from knowledge_write import write_knowledge


def test_write_with_trace_id_persists_frontmatter_and_index(tmp_path):
    result = write_knowledge("lesson", "Trace lesson", "trace-aware", trace_id="trace-123", vault_path=tmp_path)

    assert result["ok"], result
    document_path = Path(result["document"]["path"])
    frontmatter = document_path.read_text(encoding="utf-8").split("---", 2)[1]
    index = json.loads((tmp_path / "AI-Vault" / ".knowledge-index.yaml").read_text(encoding="utf-8"))

    assert 'trace_id: "trace-123"' in frontmatter
    assert index["documents"][0]["trace_id"] == "trace-123"


def test_write_without_trace_id_preserves_legacy_shape(tmp_path):
    result = write_knowledge("lesson", "Legacy shape", "compatible", vault_path=tmp_path)

    assert result["ok"], result
    document_path = Path(result["document"]["path"])
    index = json.loads((tmp_path / "AI-Vault" / ".knowledge-index.yaml").read_text(encoding="utf-8"))

    assert "trace_id:" not in document_path.read_text(encoding="utf-8")
    assert "trace_id" not in index["documents"][0]


def test_legacy_document_and_index_without_trace_id_are_readable(tmp_path):
    root = tmp_path / "AI-Vault"
    document = root / "Knowledge" / "legacy.md"
    document.parent.mkdir(parents=True)
    document.write_text(
        '---\ntitle: "Legacy document"\ntype: "lesson"\nproject_id: "p1"\n'
        'date: "2026-01-01"\nstatus: "active"\ntags: ["legacy"]\n---\n\nold body\n',
        encoding="utf-8",
    )
    (root / ".knowledge-index.yaml").write_text(
        json.dumps({"last_indexed": "2026-01-01T00:00:00+00:00", "documents": [{
            "path": "Knowledge/legacy.md", "title": "Legacy document", "type": "lesson",
            "project_id": "p1", "status": "active", "tags": ["legacy"], "date": "2026-01-01",
        }]}),
        encoding="utf-8",
    )

    read_result = read_knowledge("lesson", "legacy", vault_path=tmp_path)
    search_result = search_knowledge("old body", vault_path=tmp_path, status="active")

    assert read_result["ok"], read_result
    assert search_result["ok"], search_result
    assert search_result["total"] == 1


def test_read_new_document_returns_trace_id(tmp_path):
    result = write_knowledge("lesson", "Readable trace", "body", trace_id="trace-read", vault_path=tmp_path)

    read_result = read_knowledge("lesson", "readable-trace", vault_path=tmp_path)

    assert result["ok"], result
    assert read_result["ok"], read_result
    assert read_result["document"]["frontmatter"]["trace_id"] == "trace-read"
