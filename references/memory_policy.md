# Memory Policy / 记忆策略

只持久化可复用的项目上下文、决策、结果、测试摘要与经验。execution-report/test-result 仅保存 Summary、Metrics、Artifacts 路径列表；不保存 raw stdout、raw stderr 或 full diff。覆盖写入必须显式 `overwrite=true`。
