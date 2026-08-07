# Metadata Index v1.2

`.knowledge-index.yaml` 位于 `AI-Vault/` 根目录。虽然扩展名为 YAML，当前实现
写入 JSON-compatible YAML，以便不引入额外解析依赖。

## Schema

- `last_indexed`: 最近一次成功增量更新的 UTC ISO-8601 时间戳。
- `documents`: 文档 entry 数组。
- `path`: 相对于 `AI-Vault/` 的 Markdown 路径。
- `title`: 文档标题。
- `type`: 六种受支持的知识文档类型之一。
- `project_id`: 所属项目标识，可为空字符串。
- `tags`: 标签字符串数组。
- `status`: 文档状态字符串，写入时必有该字段。
- `date`: 文档写入日期，格式为 `YYYY-MM-DD`。
- `trace_id`: 可选的 Trace Context 标识。仅当写入请求提供非空 `trace_id` 时写入
  frontmatter 和索引 entry；旧文档和旧索引 entry 可以缺少该字段。

## Filtering semantics

`--tag`、`--status`、`--project` 均为精确匹配；多个过滤器按 AND 组合。
`--tag` 匹配 `tags` 数组中的任一项。过滤在索引元数据上执行，之后仍按原有
`query` 和 `scope` 规则搜索正文/frontmatter。无过滤参数时保持 v1.0 的全文、标签
和项目 scope 行为。

v1.1 搜索结果新增 `results`、`total`、`filtered_by`，每个 result 只暴露上述
索引字段；为兼容 M0.1，响应同时保留 `documents` 和 `metadata.count`。

## v1.2 semantic boundary

v1.1 的索引提供稳定的文档元数据和路径集合，但不存储 embedding。v1.2 可以在
此索引之上增加 embedding/vector sidecar，并复用 `path` 作为文档与语义结果的
稳定关联键；元数据过滤应继续先于 semantic ranking 执行。
