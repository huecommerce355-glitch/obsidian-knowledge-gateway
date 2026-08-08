# Vault Structure / Vault 结构

Vault 根由 `OBSIDIAN_VAULT_PATH`（仅当存在时）或 `~/Documents/Obsidian Vault` 决定。所有知识位于 `AI-Vault/`：Projects、Agents、Skills、Decisions、Execution-Reports、Reviews、Knowledge、Prompts，以及权限为 600 的 `.knowledge-index.yaml`。目录 750、Markdown 640。

`Reviews/` 保存 v1.3 `review-result` 文档，文件名为 `<date>-<task_id>-review.md`。其 frontmatter 必须包含 `review_id`、`task_id`、`trace_id`、`execution_agent`、`review_agent`、`review_mode`、`decision`、`score`，以及通用的 `title/type/project_id/date/status/tags`。

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
  - path: "Reviews/2026-01-01-task-1-review.md"
    title: "Review task-1"
    type: "review-result"
    project_id: "project-1"
    review_id: "review-1"
    task_id: "task-1"
    trace_id: "trace-1"
    execution_agent: "executor"
    review_agent: "reviewer"
    review_mode: "standard"
    decision: "PASS"
    score: 9
    tags: ["review"]
    status: "active"
    date: "2026-01-01"
```

`path` 相对于 `AI-Vault/`；过滤器对 `tag`、`status`、`project` 做精确匹配。
