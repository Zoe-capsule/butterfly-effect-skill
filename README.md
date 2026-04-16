# 🦋 Butterfly Effect Skill 蝴蝶效应技能 🦋

> **Global Dependency Scanner - Predict Chain Reactions Before Changes**
> **全局依赖扫描器 - 执行变更前先预判连锁反应**

---

## 🤖 Why Should Agents Use This Skill?
## 🤖 Agent 为什么要用这个 Skill？

### Problem Scenarios
### 问题场景

**Common Problems Agents Face:**
**Agent经常遇到的问题：**

- Delete file → System crashes (forgot to check dependencies)
- 删除文件 → 系统崩溃（忘记检查依赖）

- Modify config → Service fails to start (unknown impact scope)
- 修改配置 → 服务无法启动（不知道影响范围）

- Clean redundant files → Features break (accidentally deleted dependencies)
- 清理冗余 → 功能失效（误删依赖项）

- Refactor code → User reports errors (missed references)
- 重构代码 → 用户报错（遗漏引用）

**Root Cause:** Failed to predict chain reactions.
**根本原因：** 没有预判连锁反应。

---

### Solution
### 解决方案

**This Skill Helps You:**
**这个 Skill 帮你做到：**

- ✅ Scan dependencies before execution
- ✅ 执行前先扫描依赖

- ✅ Discover potential chain reactions
- ✅ 发现潜在连锁反应

- ✅ Risk classification (HIGH/MEDIUM/LOW)
- ✅ 风险分级（HIGH/MEDIUM/LOW）

- ✅ Generate action recommendations
- ✅ 生成建议操作清单

**Result:** Avoid the "delete → crash → fix" vicious cycle.
**效果：** 避免"删除→崩溃→补救"的恶性循环。

---

## 🔴 Red Line Rules (Mandatory)
## 🔴 红线规则（强制执行）

**Must Run This Skill Before:**
**以下场景必须先运行此 Skill：**

| Scenario | Trigger Condition | Action |
| 场景 | 触发条件 | 动作 |
|------|----------|------|
| Delete files / 删除文件 | Before deleting any file / 删除任何文件前 | Scan filename / 扫描文件名 |
| Modify config / 修改配置 | Before modifying .json/.yaml/.xml / 修改 .json/.yaml/.xml 前 | Scan config name / 扫描配置名 |
| Architecture adjustment / 架构调整 | Before moving/renaming modules / 移动/重命名模块前 | Scan module name / 扫描模块名 |
| Clean redundant / 清理冗余 | Before deleting "seemingly useless" items / 删除"看起来无用"的东西前 | Scan target items / 扫描待删除项 |

**Iron Law:**
**铁律：**
```
NO DELETION WITHOUT SCANNING FIRST
禁止未扫描先删除
```

---

## 🎯 Agent Trigger Scenarios
## 🎯 Agent 触发场景列表

### Trigger Keywords
### 触发关键词

When user says these keywords → Immediately invoke this Skill:
当用户说以下关键词时 → 立即调用此 Skill：

| Keyword / 关键词 | Scenario / 场景 |
|------|------|
| "delete/remove/clean" / "删除/移除/清理" | Before deletion / 删除操作前 |
| "modify config/change config" / "修改配置/改配置" | Before config change / 配置变更前 |
| "refactor/adjust architecture" / "重构/调整架构" | Before architecture change / 架构调整前 |
| "close/stop service" / "关闭/停止服务" | Before service stop / 服务停止前 |
| "uninstall/remove module" / "卸载/移除模块" | Before module removal / 模块移除前 |

---

## 📊 Example Results
## 📊 效果示例

### Case: Deleting memory-service
### 案例：删除 memory-service

**Scan Results** (6736 files, 23 dependencies found):
**扫描结果**（6736个文件，发现23个依赖）：

```markdown
# Butterfly Effect Scan Report / 蝴蝶效应扫描报告

**Target / 目标**: memory_service.py
**Scan Time / 扫描时间**: 2026-04-16 10:39 GMT+8
**Scan Scope / 扫描范围**: workspace (with subdirectories) / workspace（含子目录）

## Dependencies Found / 发现的依赖项（23个）

### 🔴 [HIGH] High Impact (5) - Must Handle / 高影响（5个）- 必须处理
| File / 文件 | Type / 类型 | Reference / 引用位置 | Action / 建议处理 |
|------|------|----------|------|
| startup_checklist.md | checklist | Line 7 / 第7行 | Must remove health check / 必须移除健康检查 |
| scheduled_task.xml | task | Line 12 / 第12行 | Must delete Windows task / 必须删除Windows任务 |
| health_check.ps1 | script | Line 3 / 第3行 | Must remove startup logic / 必须移除启动逻辑 |
| gateway_config.json | config | Port 8765 / 端口8765 | Must remove port config / 必须移除端口配置 |
| api_client.py | code | import memory_service | Must update reference / 必须更新引用 |

### 🟡 [MEDIUM] Medium Impact (10) - Recommended / 中影响（10个）- 建议处理
| File / 文件 | Type / 类型 | Reference / 引用位置 | Action / 建议处理 |
|------|------|----------|------|
| README.md | doc | API description / API说明 | Update docs / 更新文档 |
| usage_guide.md | doc | Example code / 示例代码 | Update examples / 更新示例 |
| ... | ... | ... | Recommended update / 建议更新 |

### 🟢 [LOW] Low Impact (8) - Can Keep / 低影响（8个）- 可保留
| File / 文件 | Type / 类型 | Reference / 引用位置 | Action / 建议处理 |
|------|------|----------|------|
| memory/history.log | implicit | History record / 历史记录 | Can archive / 可保留归档 |
| ... | ... | ... | Can keep / 可保留 |

## Recommended Action Order / 建议操作顺序
1. ✅ Handle [HIGH] first (5 items) / 先处理[HIGH]高影响（5个）
2. ⚠️ Handle [MEDIUM] next (10 items) / 再处理[MEDIUM]中影响（10个）
3. 📋 [LOW] can be kept (8 items) / [LOW]低影响可保留（8个）
4. 🔍 Re-scan after handling to confirm no residue / 处理后再次扫描确认无残留

## Scan Coverage Verification / 扫描完整性验证
- [OK] code dependencies: scanned (2) / code依赖：已扫描（2个）
- [OK] script dependencies: scanned (3) / script依赖：已扫描（3个）
- [OK] doc dependencies: scanned (8) / doc依赖：已扫描（8个）
- [OK] config dependencies: scanned (4) / config依赖：已扫描（4个）
- [OK] task dependencies: scanned (2) / task依赖：已扫描（2个）
- [OK] checklist dependencies: scanned (1) / checklist依赖：已扫描（1个）
- [OK] implicit dependencies: scanned (4) / implicit依赖：已扫描（4个）

**Scan Coverage / 扫描覆盖率**: 100%
```

---

### Comparison Effect
### 对比效果

**Without Scanning:**
**没有扫描的后果：**
```
Delete memory_service.py
↓
System startup fails (service not found)
↓
Health check errors (port 8765 doesn't exist)
↓
Windows task fails (scheduled_task.xml reference)
↓
User errors (API call fails)
↓
Emergency fix → 3 hours debugging
↓
系统启动失败（找不到服务）
↓
健康检查报错（端口8765不存在）
↓
Windows任务失败（scheduled_task.xml引用）
↓
用户报错（API调用失败）
↓
紧急补救 → 花费3小时排查
```

**With Scanning:**
**使用扫描的效果：**
```
Run butterfly_scan.py memory_service.py
↓
Found 23 dependencies (HIGH: 5)
↓
Handle dependencies one by one
↓
Delete memory_service.py
↓
Re-scan to confirm no residue
↓
System runs normally ✅
↓
15 min prevention → Avoid 3 hours fix
↓
发现23个依赖（HIGH 5个）
↓
逐个处理依赖
↓
删除 memory_service.py
↓
再次扫描确认无残留
↓
系统正常运行 ✅
↓
花费15分钟预防 → 避免3小时补救
```

---

## 🧠 How It Works
## 🧠 工作原理

### Scan Process
### 扫描流程

```
┌─────────────────────────────────────────────────────────────┐
│            Butterfly Effect Scan Process / 蝴蝶效应扫描流程        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Receive Target / 接收目标                                 │
│     └─ User input: filename/config/module name               │
│     └─ 用户输入：文件名/配置名/模块名                            │
│                                                             │
│  2. Global Scan (7 Types) / 全局扫描（7种类型）                  │
│     ├─ code:    import statements, function calls            │
│     ├─ script:  startup commands, call chains                │
│     ├─ doc:     documentation, examples                      │
│     ├─ config:  path references, URLs                        │
│     ├─ task:    Cron, Windows Task Scheduler                 │
│     ├─ checklist: startup checks, health checks              │
│     └─ implicit: history records, user habits                │
│     ├─ code:    import语句、函数调用                            │
│     ├─ script:  启动命令、调用链                                │
│     ├─ doc:     说明文档、示例                                  │
│     ├─ config:  路径引用、URL                                  │
│     ├─ task:    Cron、Windows任务计划                          │
│     ├─ checklist: 启动检查、健康检查                            │
│     └─ implicit: 历史记录、用户习惯                             │
│                                                             │
│  3. Smart Classification (Risk Assessment) / 智能分类（风险评估） │
│     ├─ HIGH:   startup/health/cron/gateway/service            │
│     ├─ MEDIUM: readme/guide/example/tutorial                  │
│     └─ LOW:    memory/history/archive/log                     │
│     ├─ HIGH:   startup/health/cron/gateway/service           │
│     ├─ MEDIUM: readme/guide/example/tutorial                 │
│     └─ LOW:    memory/history/archive/log                    │
│                                                             │
│  4. Generate Report / 生成报告                                │
│     ├─ Markdown report (human readable)                      │
│     ├─ JSON report (Agent parseable)                         │
│     └─ Visualization chart (HTML dependency graph)           │
│     ├─ Markdown报告（人类阅读）                                │
│     ├─ JSON报告（Agent解析）                                   │
│     └─ 可视化图表（HTML依赖关系图）                             │
│                                                             │
│  5. Provide Recommendations / 提供建议                        │
│     └─ Action order + verification checklist                 │
│     └─ 处理顺序 + 验证清单                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Risk Assessment Algorithm
### 风险评估算法

**Dynamic Risk Scoring:**
**动态风险评分：**

```python
def calculate_risk(file_path, reference_type):
    score = 0
    
    # Base Risk (Type Weight) / 基础风险（类型权重）
    type_weights = {
        'code': 30,
        'script': 25,
        'config': 20,
        'task': 25,
        'checklist': 30,
        'doc': 10,
        'implicit': 5
    }
    score += type_weights.get(reference_type, 10)
    
    # Keyword Risk / 关键词风险
    high_keywords = ['startup', 'health', 'cron', 'gateway', 'service', 'task']
    for keyword in high_keywords:
        if keyword in file_path.lower():
            score += 20
    
    # Historical Failure Data (Dynamic Adjustment) / 历史失败数据（动态调整）
    if has_failed_in_history(file_path):
        score += 15
    
    # Classification / 分级
    if score >= 50: return 'HIGH'
    if score >= 30: return 'MEDIUM'
    return 'LOW'
```

---

### Incremental Scan Mechanism
### 增量扫描机制

**Cache Strategy:**
**缓存策略：**

```
First Scan / 首次扫描：
  Scan 6736 files → Takes 5 min → Cache results
  扫描6736个文件 → 耗时5分钟 → 缓存结果

Incremental Scan (Recommended) / 增量扫描（推荐）：
  Detect changed files → Scan only changes → Takes 30 sec → Update cache
  检测变更文件 → 只扫描变更 → 耗时30秒 → 更新缓存
  (10x Performance Boost) / （性能提升10倍）
```

---

## 📁 Repository Structure
## 📁 仓库结构

```
butterfly-effect-skill/
│
├── README.md                 # README (Human + Agent Friendly) / 自述文件（人类+Agent友好）
├── SKILL.md                  # Skill Core Doc (OpenClaw Format) / Skill核心文档（OpenClaw格式）
├── LICENSE                   # MIT License / MIT许可证
│
├── scripts/                  # Scripts Directory / 脚本目录
│   ├── butterfly_scan.py     # 🔍 Core Scan Script (22KB, v3.0) / 核心扫描脚本（22KB，v3.0）
│   └── butterfly_visualize.py # 📊 Visualization Report (6KB) / 可视化报告生成（6KB）
│
├── references/               # Reference Docs / 参考文档目录
│   ├── scan_types.md         # 📋 Scan Type Details (7 Types) / 扫描类型详细说明（7种）
│   ├── config_template.yaml  # ⚙️ Config Template / 配置文件模板
│   └ ci_cd_templates.yml     # 🔧 CI/CD Templates (4 Types) / CI/CD集成模板（4种）
│
├── .butterfly.yaml           # 🎯 Config Example (Incremental + Cache) / 配置示例（增量扫描+缓存）
│
└── tests/                    # Test Directory (Optional) / 测试目录（可选）
    └── test_scan.py          # Unit Test / 单元测试
```

---

### File Description
### 文件说明

| File / 文件 | Size / 大小 | Description / 说明 | Required / 必须 |
|------|------|------|------|
| README.md | 6KB | README file / 自述文件 | ✅ |
| SKILL.md | 4KB | Skill core doc / Skill核心文档 | ✅ |
| butterfly_scan.py | 22KB | Core scan script / 核心扫描脚本 | ✅ |
| butterfly_visualize.py | 6KB | Visualization report / 可视化报告 | ⚪ |
| scan_types.md | 5KB | Scan type details / 扫描类型说明 | ⚪ |
| config_template.yaml | 1KB | Config template / 配置模板 | ⚪ |
| ci_cd_templates.yml | 2KB | CI/CD templates / CI/CD模板 | ⚪ |
| .butterfly.yaml | 669B | Config example / 配置示例 | ⚪ |

---

## 📦 Installation
## 📦 安装方法

### Method 1: OpenClaw Skill Installation (Recommended)
### 方法1：OpenClaw Skill安装（推荐）

```bash
# Install Skill (OpenClaw Users) / 安装 Skill（OpenClaw用户）
npx skills add Zoe-capsule/butterfly-effect-skill

# Verify Installation / 验证安装
npx skills list | grep butterfly
```

---

### Method 2: Manual Installation
### 方法2：手动安装

```bash
# 1. Clone Repository / 克隆仓库
git clone https://github.com/Zoe-capsule/butterfly-effect-skill.git

# 2. Enter Directory / 进入目录
cd butterfly-effect-skill

# 3. Install Dependencies (Optional) / 安装依赖（可选）
pip install -r requirements.txt  # If available / 如果有

# 4. Test Run / 测试运行
python scripts/butterfly_scan.py --test

# 5. View Help / 查看帮助
python scripts/butterfly_scan.py --help
```

---

### Method 3: Integrate as Subdirectory
### 方法3：作为子目录集成

```bash
# Add to Existing Project / 在现有项目中添加
mkdir -p skills/
git subtree add --prefix=skills/butterfly-effect https://github.com/Zoe-capsule/butterfly-effect-skill.git main

# Or Copy Directly / 或直接复制
cp -r butterfly-effect-skill skills/butterfly-effect
```

---

### Configuration
### 配置

**Create Config File:**
**创建配置文件：**

```bash
# Copy Config Template / 复制配置模板
cp references/config_template.yaml .butterfly.yaml

# Edit Config / 编辑配置
nano .butterfly.yaml
```

**Config Example:**
**配置示例：**

```yaml
# .butterfly.yaml
scan:
  incremental: true    # Enable incremental scan / 启用增量扫描（推荐）
  cache: true          # Enable cache / 启用缓存
  cache_dir: .cache/   # Cache directory / 缓存目录
  
types:
  code: true           # Scan code dependencies / 扫描代码依赖
  script: true         # Scan script dependencies / 扫描脚本依赖
  config: true         # Scan config dependencies / 扫描配置依赖
  task: true           # Scan task dependencies / 扫描任务依赖
  doc: true            # Scan doc dependencies / 扫描文档依赖
  checklist: true      # Scan checklist dependencies / 扫描检查清单
  implicit: true       # Scan implicit dependencies / 扫描隐式依赖

output:
  format: markdown     # Output format / 输出格式（markdown/json/html）
  file: report.md      # Output file / 输出文件
```

---

## ⚡ Quick Usage
## ⚡ 快速使用

### Basic Usage
### 基本用法

```bash
# Scan Target (Recommended: Incremental) / 扫描目标（推荐增量扫描）
python butterfly-effect/scripts/butterfly_scan.py <target> --incremental

# Output JSON (Agent Parseable) / 输出JSON（方便解析）
python butterfly-effect/scripts/butterfly_scan.py <target> --format json --output report.json

# Disable Cache (First Scan) / 禁用缓存（首次扫描）
python butterfly-effect/scripts/butterfly_scan.py <target> --no-cache
```

---

### Output Format
### 输出格式

**Markdown Report:**
**Markdown报告：**
```markdown
# Butterfly Effect Scan Report / 蝴蝶效应扫描报告

## Dependencies Found: 23 / 发现依赖项: 23个
- 🔴 HIGH: 5 (Must Handle) / 高影响（5个）- 必须处理
- 🟡 MEDIUM: 10 (Recommended) / 中影响（10个）- 建议处理
- 🟢 LOW: 8 (Can Keep) / 低影响（8个）- 可保留

## Recommended Actions / 建议操作
1. Handle HIGH dependencies first / 先处理 HIGH 级依赖
2. Handle MEDIUM dependencies next / 再处理 MEDIUM 级依赖
3. Execute changes / 执行变更
4. Re-scan to confirm no residue / 再次扫描确认无残留
```

**JSON Report (Agent Parseable):**
**JSON报告**（方便Agent解析）：
```json
{
  "target": "memory-service",
  "dependencies": [...],
  "high_count": 5,
  "medium_count": 10,
  "low_count": 8,
  "action_required": true
}
```

---

## 🧠 Smart Features
## 🧠 智能功能

| Feature / 功能 | Description / 说明 | Effect / 效果 |
|------|------|------|
| **Incremental Scan / 增量扫描** | Scan only changed files / 只扫描变更文件 | Reduce 90% time / 减少90%时间 |
| **Dynamic Risk Assessment / 动态风险评估** | Based on historical failure data / 基于历史失败数据 | Reduce false alarms / 减少误报 |
| **Historical Database / 历史数据库** | Record every scan result / 记录每次扫描结果 | Avoid duplicate scans / 避免重复扫描 |
| **CI/CD Integration / CI/CD集成** | Automated pipeline / 自动化流水线 | Force check before changes / 变更前强制检查 |

---

## 🔗 Related Resources
## 🔗 相关资源

| Resource / 资源 | Link / 链接 |
|------|------|
| Main Repo / 主仓库 | https://github.com/Zoe-capsule/butterfly-effect-skill |
| Skill Catalog / 技能目录 | https://github.com/Zoe-capsule/zoe-skills |

---

## ⭐ Why Worth Starring?
## ⭐ 为什么值得星标？

**Agent Value:**
**Agent 价值：**

- ✅ Avoid post-deletion crashes (reduce mistakes) / 避免删除后崩溃（减少失误）
- ✅ Predict risks before execution (improve professionalism) / 执行前预判风险（提升专业性）
- ✅ Closed-loop verification (build trust) / 闭环验证（建立信任）
- ✅ Smart risk assessment (reduce false alarms) / 智能风险评估（减少误报）

**Developer Value:**
**开发价值：**

- ✅ v3.0 Complete optimization (incremental + cache + dynamic risk) / v3.0完整优化（增量扫描+缓存+动态风险）
- ✅ CI/CD integration templates (automated pipeline) / CI/CD集成模板（自动化流水线）
- ✅ Visualization reports (HTML dependency graph) / 可视化报告（HTML依赖关系图）
- ✅ Open source & free (MIT License) / 开源免费（MIT许可）

---

**Butterfly Effect v3.0 - Make Changes Safer / 让变更更安全** ✅

---

## 👤 Author
## 👤 作者

**Ye Qingze / 叶清泽**

- GitHub: https://github.com/Zoe-capsule
- Skill Catalog / 技能目录: https://github.com/Zoe-capsule/zoe-skills

---

**MIT License © 2026 Ye Qingze / MIT License © 2026 叶清泽**