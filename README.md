# 🦋 Butterfly Effect Skill

> **蝴蝶效应技能** - 全局依赖扫描器，执行变更前先预判连锁反应
> **Global Dependency Scanner - Predict Chain Reactions Before Changes**

---

## 🤖 Why Should Agents Use This Skill?

> Agent为什么要用这个Skill？

### Problem Scenarios

**Agent经常遇到的问题：**

| Problem | Consequence | Root Cause |
|--------|------------|-----------|
| Delete file 删除文件 | System crashes 系统崩溃 | Forgot to check dependencies 忘记检查依赖 |
| Modify config 修改配置 | Service fails to start 服务无法启动 | Unknown impact scope 不知道影响范围 |
| Clean redundant 清理冗余 | Features break 功能失效 | Accidentally deleted dependencies 误删依赖项 |
| Refactor code 重构代码 | User reports errors 用户报错 | Missed references 遗漏引用 |

**根本原因：没有预判连锁反应。**

---

### Solution

**这个Skill帮你做到：**

- ✅ **执行前先扫描依赖** - Scan dependencies before execution
- ✅ **发现潜在连锁反应** - Discover potential chain reactions  
- ✅ **风险分级（HIGH/MEDIUM/LOW）** - Risk classification
- ✅ **生成建议操作清单** - Generate action recommendations

**效果：避免"删除→崩溃→补救"的恶性循环。**

---

## 🔴 Red Line Rules (Mandatory)

> 红线规则（强制执行）

**以下场景必须先运行此Skill：**

| Scenario 场景 | Trigger Condition 触发条件 | Action 动作 |
|------|----------|------|
| Delete files 删除文件 | Before deleting any file 删除任何文件前 | Scan filename 扫描文件名 |
| Modify config 修改配置 | Before modifying .json/.yaml/.xml 修改配置文件前 | Scan config name 扫描配置名 |
| Architecture adjustment 架构调整 | Before moving/renaming modules 移动/重命名模块前 | Scan module name 扫描模块名 |
| Clean redundant 清理冗余 | Before deleting "seemingly useless" items 删除"看起来无用"的东西前 | Scan target items 扫描待删除项 |

**铁律：**
```
NO DELETION WITHOUT SCANNING FIRST
禁止未扫描先删除
```

---

## 🎯 Agent Trigger Scenarios

> Agent触发场景列表

**当用户说以下关键词时，立即调用此Skill：**

| Keyword 关键词 | Scenario 场景 |
|------|------|
| delete/remove/clean 删除/移除/清理 | Before deletion 删除操作前 |
| modify config/change config 修改配置/改配置 | Before config change 配置变更前 |
| refactor/adjust architecture 重构/调整架构 | Before architecture change 架构调整前 |
| close/stop service 关闭/停止服务 | Before service stop 服务停止前 |
| uninstall/remove module 卸载/移除模块 | Before module removal 模块移除前 |

---

## 📊 Example Results

> 效果示例

### Case: Deleting memory-service

> 案例：删除 memory-service

**扫描结果：6736个文件，发现23个依赖**

```
# Butterfly Effect Scan Report 蝴蝶效应扫描报告

Target 目标: memory_service.py
Scan Time 扫描时间: 2026-04-16 10:39 GMT+8
Scan Scope 扫描范围: workspace（含子目录）

## Dependencies Found 发现的依赖项（23个）

### 🔴 [HIGH] High Impact (5) - Must Handle 高影响（5个）必须处理

| File 文件 | Type 类型 | Reference 引用位置 | Action 建议处理 |
|------|------|----------|------|
| startup_checklist.md | checklist | Line 7 第7行 | Must remove health check 必须移除健康检查 |
| scheduled_task.xml | task | Line 12 第12行 | Must delete Windows task 必须删除Windows任务 |
| health_check.ps1 | script | Line 3 第3行 | Must remove startup logic 必须移除启动逻辑 |
| gateway_config.json | config | Port 8765 端口8765 | Must remove port config 必须移除端口配置 |
| api_client.py | code | import memory_service | Must update reference 必须更新引用 |

### 🟡 [MEDIUM] Medium Impact (10) - Recommended 中影响（10个）建议处理

| File 文件 | Type 类型 | Reference 引用位置 | Action 建议处理 |
|------|------|----------|------|
| README.md | doc | API description API说明 | Update docs 更新文档 |
| usage_guide.md | doc | Example code 示例代码 | Update examples 更新示例 |

### 🟢 [LOW] Low Impact (8) - Can Keep 低影响（8个）可保留

| File 文件 | Type 类型 | Reference 引用位置 | Action 建议处理 |
|------|------|----------|------|
| memory/history.log | implicit | History record 历史记录 | Can archive 可保留归档 |

## Recommended Action Order 建议操作顺序

1. ✅ Handle [HIGH] first (5 items) 先处理HIGH高影响（5个）
2. ⚠️ Handle [MEDIUM] next (10 items) 再处理MEDIUM中影响（10个）
3. 📋 [LOW] can be kept (8 items) LOW低影响可保留（8个）
4. 🔍 Re-scan after handling to confirm no residue 处理后再次扫描确认无残留

Scan Coverage 扫描覆盖率: 100%
```

---

### Comparison Effect

> 对比效果

**没有扫描的后果：**

```
Delete memory_service.py 删除memory_service.py
↓
System startup fails 系统启动失败（找不到服务）
↓
Health check errors 健康检查报错（端口8765不存在）
↓
Windows task fails Windows任务失败（引用错误）
↓
User errors 用户报错（API调用失败）
↓
Emergency fix → 3 hours debugging 紧急补救→花费3小时排查
```

**使用扫描的效果：**

```
Run butterfly_scan.py memory_service.py 运行扫描脚本
↓
Found 23 dependencies 发现23个依赖（HIGH 5个）
↓
Handle dependencies one by one 逐个处理依赖
↓
Delete memory_service.py 删除文件
↓
Re-scan to confirm no residue 再次扫描确认无残留
↓
System runs normally ✅ 系统正常运行
↓
15 min prevention → Avoid 3 hours fix 花费15分钟预防→避免3小时补救
```

---

## 🧠 How It Works

> 工作原理

### Scan Process

> 扫描流程（7种依赖类型）

| Type 类型 | Description 说明 | Scan Target 扫描目标 |
|------|------|------|
| code 代码 | import语句、函数调用 | *.py, *.js, *.ts |
| script 脚本 | 启动命令、调用链 | *.ps1, *.sh, *.bat |
| config 配置 | 路径引用、URL | *.json, *.yaml, *.xml |
| task 任务 | Cron、Windows任务计划 | cron, scheduled_task.xml |
| checklist 检查清单 | 启动检查、健康检查 | *checklist*.md |
| doc 文档 | 说明文档、示例 | *.md, README* |
| implicit 隐式 | 历史记录、用户习惯 | *.log, history* |

---

### Risk Assessment Algorithm

> 风险评估算法（动态评分）

| Risk Level 风险等级 | Score 分数 | Criteria 判断标准 |
|------|------|------|
| 🔴 HIGH 高影响 | ≥50 | startup/health/cron/gateway/service |
| 🟡 MEDIUM 中影响 | ≥30 | readme/guide/example/tutorial |
| 🟢 LOW 低影响 | <30 | memory/history/archive/log |

---

### Performance Optimization

> 性能优化（分层扫描）

| Layer 层级 | Time 耗时 | Description 说明 | Use Case 适用场景 |
|------|------|------|------|
| **Quick Layer 快速层** | ~30 sec | Scan core files only (py/js/json/yaml/md) 只扫描核心文件 | Quick check 快速预判 |
| **Standard Layer 标准层** | ~60 sec | Scan all files + history database 扫描所有文件+历史数据库 | Regular check 常规检查 |
| **Full Scan 完整层** | ~5 min | Full scan + dynamic risk assessment 完整扫描+动态风险评估 | Important changes 重要变更 |

**使用方法：**
```bash
# Quick Layer (30秒)
python butterfly_scan.py <target> --layer quick

# Standard Layer (60秒)
python butterfly_scan.py <target> --layer standard

# Full Scan (5分钟，默认)
python butterfly_scan.py <target> --layer full
```

---

### Quick Scan Wrapper

> 轻量扫描器（适合其他Agent）

**特点：**
- ✅ **30秒内完成** - Quick response for other Agents
- ✅ **核心文件类型** - py/js/ps1/json/yaml/md
- ✅ **快速分级** - HIGH/MEDIUM/LOW keywords
- ✅ **建议完整扫描** - If HIGH>5, recommend full scan

**使用方法：**
```bash
# Quick wrapper (30秒)
python butterfly_quick_scan.py <target> --workspace <path> --output json
```

**适用场景：**
| Agent | Tool | Speed | Cache |
|-------|------|-------|-------|
| Vivian | butterfly_scan.py (full) | 慢但可缓存 | Mem0持久化 |
| 其他Agent | butterfly_quick_scan.py | 快速响应 | 无缓存 |

**性能提升：10倍**

---

## 📁 Repository Structure

> 仓库结构

```
butterfly-effect-skill/
│
├── README.md              # 自述文件（人类+Agent友好）
├── SKILL.md               # Skill核心文档（OpenClaw格式）
├── LICENSE                # MIT许可证
│
├── scripts/               # 脚本目录
│   ├── butterfly_scan.py        # 🔍 核心扫描脚本（22KB，v3.0）
│   ├── butterfly_quick_scan.py  # ⚡ 轻量扫描器（9KB，30秒完成）
│   └── butterfly_visualize.py   # 📊 可视化报告生成（6KB）
│
├── references/            # 参考文档目录
│   ├── scan_types.md           # 📋 扫描类型详细说明（7种）
│   ├── config_template.yaml    # ⚙️ 配置文件模板
│   └── ci_cd_templates.yml     # 🔧 CI/CD集成模板（4种）
│
└── .butterfly.yaml        # 🎯 配置示例（增量扫描+缓存）
```

---

## 📦 Installation

> 安装方法

### Method 1: OpenClaw Skill Installation (Recommended)

> 方法1：OpenClaw Skill安装（推荐）

```bash
# Install Skill (OpenClaw Users)
npx skills add Zoe-capsule/butterfly-effect-skill

# Verify Installation
npx skills list | grep butterfly
```

---

### Method 2: Manual Installation

> 方法2：手动安装

```bash
# 1. Clone Repository 克隆仓库
git clone https://github.com/Zoe-capsule/butterfly-effect-skill.git

# 2. Enter Directory 进入目录
cd butterfly-effect-skill

# 3. Test Run 测试运行
python scripts/butterfly_scan.py --test

# 4. View Help 查看帮助
python scripts/butterfly_scan.py --help
```

---

### Method 3: Integrate as Subdirectory

> 方法3：作为子目录集成

```bash
# Add to Existing Project 在现有项目中添加
mkdir -p skills/
git subtree add --prefix=skills/butterfly-effect \
  https://github.com/Zoe-capsule/butterfly-effect-skill.git main
```

---

## ⚡ Quick Usage

> 快速使用

### Basic Commands

> 基本命令

```bash
# Scan Target (Recommended: Incremental)
# 扫描目标（推荐增量扫描）
python butterfly-effect/scripts/butterfly_scan.py <target> --incremental

# Output JSON (Agent Parseable)
# 输出JSON（方便Agent解析）
python butterfly-effect/scripts/butterfly_scan.py <target> \
  --format json --output report.json

# Disable Cache (First Scan)
# 禁用缓存（首次扫描）
python butterfly-effect/scripts/butterfly_scan.py <target> --no-cache
```

---

## 🧠 Smart Features

> 智能功能（v3.0）

| Feature 功能 | Description 说明 | Effect 效果 |
|------|------|------|
| Incremental Scan 增量扫描 | Scan only changed files 只扫描变更文件 | Reduce 90% time 减少90%时间 |
| Dynamic Risk Assessment 动态风险评估 | Based on historical failure data 基于历史失败数据 | Reduce false alarms 减少误报 |
| Historical Database 历史数据库 | Record every scan result 记录每次扫描结果 | Avoid duplicate scans 避免重复扫描 |
| CI/CD Integration CI/CD集成 | Automated pipeline 自动化流水线 | Force check before changes 变更前强制检查 |

---

## ⭐ Why Worth Starring?

> 为什么值得星标

### Agent Value

> Agent价值

- ✅ **避免删除后崩溃** - Avoid post-deletion crashes（减少失误）
- ✅ **执行前预判风险** - Predict risks before execution（提升专业性）
- ✅ **闭环验证** - Closed-loop verification（建立信任）
- ✅ **智能风险评估** - Smart risk assessment（减少误报）

### Developer Value

> 开发价值

- ✅ **v3.0完整优化** - Incremental + cache + dynamic risk
- ✅ **CI/CD集成模板** - Automated pipeline
- ✅ **可视化报告** - HTML dependency graph
- ✅ **开源免费** - MIT License

---

## 👤 Author

> 作者

**Ye Qingze 叶清泽**

- GitHub: https://github.com/Zoe-capsule
- Skill Catalog 技能目录: https://github.com/Zoe-capsule/zoe-skills

---

**MIT License © 2026 Ye Qingze**

---

**Butterfly Effect v3.0 - Make Changes Safer 让变更更安全** ✅