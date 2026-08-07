import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from knowledge_write import write_knowledge

def test_incremental_index_and_corruption(tmp_path):
    write_knowledge("lesson", "first", "one", vault_path=tmp_path)
    index = tmp_path / "AI-Vault" / ".knowledge-index.yaml"
    data = json.loads(index.read_text())
    assert len(data["documents"]) == 1 and data["last_indexed"]
    write_knowledge("lesson", "second", "two", vault_path=tmp_path)
    assert len(json.loads(index.read_text())["documents"]) == 2
    index.write_text("not yaml/json")
    result = write_knowledge("lesson", "third", "three", vault_path=tmp_path)
    assert result["error_code"] == "ERR-KNG-006"

