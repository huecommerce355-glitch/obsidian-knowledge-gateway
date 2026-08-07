import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from knowledge_write import write_knowledge
from knowledge_read import read_knowledge
from knowledge_search import search_knowledge

def seed(tmp_path):
    return write_knowledge("lesson", "Caching lesson", {"body": "cache improves latency"}, project_id="p1", tags=["perf", "cache"], vault_path=tmp_path)

def test_read_default_and_full(tmp_path):
    result = seed(tmp_path); path = Path(result["document"]["path"])
    short = read_knowledge("lesson", path.stem, vault_path=tmp_path)
    assert short["ok"] and "body" not in short["document"]
    full = read_knowledge("lesson", path.stem, vault_path=tmp_path, full=True)
    assert "cache improves latency" in full["document"]["body"]

def test_search_scopes(tmp_path):
    seed(tmp_path)
    assert search_knowledge("latency", "markdown", vault_path=tmp_path)["metadata"]["count"] == 1
    assert search_knowledge("perf", "tags", vault_path=tmp_path)["metadata"]["count"] == 1
    assert search_knowledge("p1", "project", vault_path=tmp_path)["metadata"]["count"] == 1

