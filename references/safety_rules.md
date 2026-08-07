# Safety Rules / 安全规则

检测 secret、`.env` 多行 KEY=value、gho_/ghp_/sk-/Bearer、邮箱/手机号/身份证，以及 `.git/`、`.obsidian/`、`.claude/`、`.claudian/` 和其他隐藏目录路径。命中直接返回 ERR-KNG-004，不做静默脱敏；任何失败均不得写盘。
