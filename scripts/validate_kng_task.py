"""Validate HACP v1.0 KNG task envelopes; Python 3.9+, stdlib only."""
import argparse, json, sys
DOC_TYPES = {"execution-report", "agent-result", "test-result", "decision-record", "project-context", "lesson", "review-result"}
OPS = {"kng.write", "kng.read", "kng.search"}
FIELDS = ("protocol", "message_id", "timestamp", "type", "source", "target", "payload", "ttl_seconds")
def validate_task(data):
    errors = []
    if not isinstance(data, dict): return [{"error_code": "ERR-KNG-007", "field": "root", "message": "Expected JSON object"}]
    for field in FIELDS:
        if field not in data: errors.append({"error_code": "ERR-KNG-003", "field": field, "message": "Missing required field"})
    if data.get("protocol") != "HACP/1.0": errors.append({"error_code": "ERR-KNG-007", "field": "protocol", "message": "Expected HACP/1.0"})
    if data.get("type") not in OPS: errors.append({"error_code": "ERR-KNG-007", "field": "type", "message": "Expected kng.write/read/search"})
    payload = data.get("payload")
    if not isinstance(payload, dict): return errors + [{"error_code": "ERR-KNG-003", "field": "payload", "message": "Payload must be an object"}]
    if data.get("type") == "kng.write":
        for field in ("doc_type", "project_id", "title", "body"):
            if not payload.get(field): errors.append({"error_code": "ERR-KNG-003", "field": "payload." + field, "message": "Required for write"})
        if payload.get("doc_type") not in DOC_TYPES: errors.append({"error_code": "ERR-KNG-002", "field": "payload.doc_type", "message": "Invalid doc_type"})
    elif data.get("type") == "kng.read":
        for field in ("doc_type", "id"):
            if not payload.get(field): errors.append({"error_code": "ERR-KNG-003", "field": "payload." + field, "message": "Required for read"})
    elif data.get("type") == "kng.search" and not payload.get("query"): errors.append({"error_code": "ERR-KNG-003", "field": "payload.query", "message": "Required for search"})
    return errors
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--input", required=True); args = parser.parse_args()
    try: data = json.load(open(args.input, encoding="utf-8")); errors = validate_task(data)
    except (OSError, ValueError) as exc: errors = [{"error_code": "ERR-KNG-007", "field": "input", "message": str(exc)}]
    result = {"valid": not errors, "errors": errors}; print(json.dumps(result, ensure_ascii=False)); return 0 if not errors else 1
if __name__ == "__main__": sys.exit(main())
