# Vault Structure / Vault 结构

Vault 根由 `OBSIDIAN_VAULT_PATH`（仅当存在时）或 `~/Documents/Obsidian Vault` 决定。所有知识位于 `AI-Vault/`：Projects、Agents、Skills、Decisions、Execution-Reports、Knowledge、Prompts，以及权限为 600 的 `.knowledge-index.yaml`。目录 750、Markdown 640。

`.knowledge-index.yaml` schema v1.1 是 JSON-compatible YAML：

```yaml
last_indexed: "2026-01-01T00:00:00+00:00"
documents:
  - path: "Decisions/ADR-001-example.md"
    title: "Example"
    type: "decision-record"
    project_id: "project-1"
    tags: ["architecture"]
    status: "accepted"
    date: "2026-01-01"
```

`path` 相对于 `AI-Vault/`；过滤器对 `tag`、`status`、`project` 做精确匹配。
