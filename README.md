# Butterfly Effect Skill

> **全局依赖扫描器 - 执行变更前先预判连锁反应**

---

## 版本历史

| 版本 | 功能 | 说明 |
|------|------|------|
| v1.0 | 基础扫描 | 7种依赖类型 + Markdown报告 |
| v2.0 | 性能优化 | 增量扫描 + 缓存 + JSON输出 + 验证 |
| v3.0 | 智能分析 | 配置文件 + 历史数据库 + 动态风险评估 |

---

## 核心功能

### 🔍 依赖扫描

扫描7种依赖类型：
- **代码依赖**：.py, .js, .ts, .go, .java
- **脚本依赖**：.ps1, .bat, .sh, .cmd
- **文档依赖**：.md, .rst, .txt
- **配置依赖**：.json, .yaml, .xml, .toml
- **任务依赖**：Cron任务, Windows任务计划
- **检查清单**：启动检查, 健康检查
- **隐式依赖**：用户习惯, 历史记录

---

### ⚡ 性能优化

| 功能 | 说明 | 效果 |
|------|------|------|
| **增量扫描** | 基于git diff只扫描变更文件 | 减少90%扫描时间 |
| **缓存机制** | 缓存上次扫描结果 | 避免重复扫描 |
| **配置文件** | .butterfly.yaml自定义配置 | 灵活控制扫描行为 |

---

### 🧠 智能分析

| 功能 | 说明 |
|------|------|
| **历史数据库** | 记录每次扫描结果 |
| **动态风险评估** | 基于历史失败数据调整风险等级 |
| **智能风险预测** | 失败次数≥5次 → 风险等级提升为HIGH |

---

## 使用方法

### 基本用法

```bash
# 全扫描
python butterfly-effect/scripts/butterfly_scan.py <target> --workspace <path>

# 增量扫描（只扫描变更文件）
python butterfly-effect/scripts/butterfly_scan.py <target> --incremental

# JSON输出
python butterfly-effect/scripts/butterfly_scan.py <target> --format json --output report.json

# 禁用缓存
python butterfly-effect/scripts/butterfly_scan.py <target> --no-cache
```

---

### 配置文件

创建 `.butterfly.yaml` 在项目根目录：

```yaml
scan:
  mode: incremental
  use_cache: true
  exclude_paths:
    - node_modules
    - __pycache__

dynamic_risk:
  enabled: true
  failure_thresholds:
    high: 5
    medium: 3
```

---

### 可视化报告

```bash
# 生成HTML可视化报告
python butterfly-effect/scripts/butterfly_visualize.py report.json --output visual.html
```

---

## 输出格式

### Markdown报告

```markdown
# 蝴蝶效应扫描报告 v3.0

## 性能统计
- 总文件: 6736
- 缓存文件: 5420
- 实际扫描: 316
- 扫描耗时: 156ms

## 动态风险评估
- 智能调整: 12个文件
- 基于历史失败数据调整风险等级
```

---

### JSON报告

```json
{
  "target": "memory-lancedb-pro",
  "dependencies": [...],
  "performance": {...},
  "dynamic_risks": [...]
}
```

---

## CI/CD集成

### GitHub Actions

```yaml
# .github/workflows/butterfly-scan.yml
name: Butterfly Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python butterfly-effect/scripts/butterfly_scan.py --incremental
```

---

## 文件结构

```
butterfly-effect/
├── README.md                    # 使用说明
├── SKILL.md                     # Skill核心文档
├── .butterfly.yaml              # 配置示例
├── scripts/
│   ├── butterfly_scan.py        # v3.0扫描脚本（完整优化）
│   └── butterfly_visualize.py   # 可视化脚本
└── references/
    ├── scan_types.md            # 扫描类型详细说明
    ├── config_template.yaml     # 配置模板（详细）
    └── ci_cd_templates.yml      # CI/CD模板（GitHub/GitLab/Jenkins）
```

---

## 适用场景

| 场景 | 使用方式 |
|------|----------|
| 删除文件 | 扫描目标文件名 |
| 修改配置 | 扫描配置文件名 |
| 架构调整 | 扫描模块名 |
| 清理冗余 | 扫描待删除项 |

---

## 特点

- ✅ **人类友好**：清晰文档、示例、可视化
- ✅ **Agent友好**：结构化JSON、触发场景列表
- ✅ **性能优化**：增量扫描、缓存机制
- ✅ **智能分析**：历史数据、动态风险评估
- ✅ **CI/CD集成**：GitHub Actions、GitLab CI、Jenkins

---

**Butterfly Effect v3.0 - 让变更更安全** ✅