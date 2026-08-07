import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from safety_filter import check

def test_sensitive_content_blocked():
    for value in ["api_key=abc", "A_TOKEN=abc\nB_SECRET=def", "ghp_12345678901234567890", "a@b.example", "13812345678", "11010519491231002X"]:
        assert check(value)["error_code"] == "ERR-KNG-004"

def test_forbidden_paths_blocked():
    for value in [".git/config", "AI-Vault/.obsidian/app.json", ".claude/x", ".claudian/x"]:
        assert check("safe", value)["error_code"] == "ERR-KNG-004"

