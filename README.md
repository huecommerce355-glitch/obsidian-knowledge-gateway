# obsidian-knowledge-gateway

Hermes Obsidian Knowledge Gateway - long-term knowledge memory layer.

- knowledge.write / read / search / index (HACP v1.0, kng.* messages)
- Safe pipeline: safety_filter enforced before every write (secret/PII/token filtering)
- Vault layout: AI-Vault/ (Projects, Agents, Skills, Decisions, Execution-Reports, Knowledge, Prompts)
- Index: frontmatter + .knowledge-index.yaml (v1.0, no database)
- Decisions: ADR-{number}-{slug}.md convention

## Tests

```bash
python3 -m pytest tests/ -v
```
