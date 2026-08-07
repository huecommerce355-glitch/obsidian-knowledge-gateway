---
name: obsidian-knowledge-gateway
description: Use for safe HACP v1.0 long-term knowledge write/read/search in an Obsidian Vault, including memory, decisions, execution summaries, and index maintenance.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [obsidian, knowledge, memory, hacp, gateway]
    related_skills: [coding-agent-gateway, github-development-gateway]
---

# Obsidian Knowledge Gateway v1.0

## Overview

基础设施层 Gateway，为 Hermes 提供长期知识记忆层，连接 Orchestrator 与 Obsidian Vault。协议为 HACP v1.0，消息前缀为 `kng.`。六类文档是 `execution-report`、`agent-result`、`test-result`、`decision-record`、`project-context`、`lesson`。

## When to Use

当需要持久化或检索项目上下文、决策、测试/执行摘要、Agent 结果或经验时使用。不要用于 GitHub 操作；委托 `github-development-gateway`。不要用于编码执行；委托 `coding-agent-gateway`。

## How to Load

先读取本文件；需要协议、目录、策略或交互细节时再读取 `references/hacp_protocol.md`、`vault_structure.md`、`memory_policy.md`、`safety_rules.md`、`gateway_interaction.md`。确定性操作使用 `scripts/knowledge_write.py`、`knowledge_read.py`、`knowledge_search.py`；任务信封先用 `validate_kng_task.py` 校验。

## Core Architecture

```text
Hermes → obsidian-knowledge-gateway → Obsidian Vault
                         └── AI-Vault/ + .knowledge-index.yaml
```

路径优先使用存在的 `OBSIDIAN_VAULT_PATH`，否则 `~/Documents/Obsidian Vault`。写入管线固定为 `safety_filter.check(content) → write → incremental index`。默认 read 只返回 path/frontmatter/summary；`full:true` 才返回 body。execution-report/test-result 丢弃 raw stdout/stderr/full diff，仅保留 Summary、Metrics、Artifacts。

## Error Codes

| Code | Meaning |
|---|---|
| ERR-KNG-001 | Vault 不可用 |
| ERR-KNG-002 | doc_type 无效 |
| ERR-KNG-003 | 必填字段缺失 |
| ERR-KNG-004 | 安全拦截 |
| ERR-KNG-005 | 文档不存在 |
| ERR-KNG-006 | 索引损坏 |
| ERR-KNG-007 | 输入无效 |

## Common Pitfalls

- 不要绕过安全过滤器，也不要把 secret 静默脱敏后保存。
- 不要把原始日志或完整 diff 放进 execution/test 文档。
- 不要直接写 Vault 根；统一写 `AI-Vault/`。
- Decisions 使用 `ADR-{number}-{slug}.md`，number 从现有最大值递增。
- 默认不覆盖已有文件；索引损坏必须报告 ERR-KNG-006。

## Verification Checklist

- [ ] `python3 scripts/validate_kng_task.py --input task.json` 返回正确 JSON 和 exit code。
- [ ] 写入前安全检查通过，失败无新文件。
- [ ] Markdown frontmatter、权限和增量索引正确。
- [ ] 默认读取无 body，搜索支持 markdown/tags/project。
- [ ] 离线测试：`python3 -m pytest tests/ -v`。

## Related Skills

`coding-agent-gateway` 负责执行，`github-development-gateway` 负责 GitHub 生命周期；本 Gateway 只负责知识层。
