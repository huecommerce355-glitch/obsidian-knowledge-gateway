"""Fail-closed content and path safety checks."""
import json, re
from pathlib import Path

SECRET = re.compile(r"(?i)(api[_-]?key|secret|token|password|private\s+key)\s*[:=]")
ENV = re.compile(r"(?m)^\s*[A-Z][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD)\s*=\S+")
CREDENTIAL = re.compile(r"(?i)(gh[op]_\w{20,}|sk-[A-Za-z0-9_-]{10,}|Bearer\s+[A-Za-z0-9._-]{10,})")
PII = re.compile(r"(?:[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:\+?86[- ]?)?1[3-9]\d{9}|\b\d{17}[\dXx]\b)")
FORBIDDEN = {".git", ".obsidian", ".claude", ".claudian"}

def _text(value): return json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
def check(content, path=None):
    text = _text(content)
    if SECRET.search(text) or ENV.search(text) or CREDENTIAL.search(text) or PII.search(text):
        return {"ok": False, "error_code": "ERR-KNG-004", "message": "content blocked by safety filter"}
    if path is not None:
        parts = Path(path).parts
        if any(part in FORBIDDEN or part.startswith(".") for part in parts):
            return {"ok": False, "error_code": "ERR-KNG-004", "message": "path blocked by safety filter"}
    return {"ok": True}
