# HACP v1.0 Protocol / 协议

请求使用 `protocol/message_id/timestamp/type/source/target/payload/trace_id?/ttl_seconds` 标准信封，操作类型为 `kng.write`、`kng.read`、`kng.search`。响应类型为 `kng.response`，字段为 `status/documents/metadata/errors`。

错误码：ERR-KNG-001 Vault 不可用；002 doc_type 无效；003 必填缺失；004 安全拦截；005 文档不存在；006 索引损坏；007 输入无效。
