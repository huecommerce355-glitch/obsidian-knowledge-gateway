import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from validate_kng_task import validate_task

BASE = {"protocol": "HACP/1.0", "message_id": "m1", "timestamp": "2026-01-01T00:00:00Z", "source": "hermes", "target": "kng", "trace_id": "tr-1", "ttl_seconds": 60}
def test_valid_operations_and_optional_trace():
    for op, payload in [("kng.write", {"doc_type": "lesson", "project_id": "p", "title": "t", "body": "b"}), ("kng.read", {"doc_type": "lesson", "id": "t"}), ("kng.search", {"query": "x"})]:
        request = dict(BASE, type=op, payload=payload)
        assert validate_task(request) == []
    no_trace = dict(BASE); no_trace.pop("trace_id"); no_trace.update(type="kng.search", payload={"query": "x"})
    assert validate_task(no_trace) == []

def test_missing_fields_fail():
    errors = validate_task({"protocol": "HACP/1.0", "type": "kng.write", "payload": {}})
    assert errors and any(e["error_code"] == "ERR-KNG-003" for e in errors)

