# Butterfly Effect Skill

> **全局依赖扫描器 - 执行变更前先预判连锁反应**

---

## 🤖 Agent 为什么要用这个 Skill？

### 问题场景

**Agent经常遇到的问题**：
- 删除文件 → 系统崩溃（忘记检查依赖）
- 修改配置 → 服务无法启动（不知道影响范围）
- 清理冗余 → 功能失效（误删依赖项）
- 重构代码 → 用户报错（遗漏引用）

**根本原因**：没有预判连锁反应。

---

### 解决方案

**这个 Skill 帮你做到**：
- ✅ 执行前先扫描依赖
- ✅ 发现潜在连锁反应
- ✅ 风险分级（HIGH/MEDIUM/LOW）
- ✅ 生成建议操作清单

**效果**：避免"删除→崩溃→补救"的恶性循环。

---

## 🔴 红线规则（强制执行）

**以下场景必须先运行此 Skill**：

| 场景 | 触发条件 | 动作 |
|------|----------|------|
| 删除文件 | 删除任何文件前 | 扫描文件名 |
| 修改配置 | 修改 .json/.yaml/.xml 前 | 扫描配置名 |
| 架构调整 | 移动/重命名模块前 | 扫描模块名 |
| 清理冗余 | 删除"看起来无用"的东西前 | 扫描待删除项 |

**铁律**：
```
NO DELETION WITHOUT SCANNING FIRST
```

---

## 🎯 Agent 触发场景列表

### 触发关键词

当用户说以下关键词时 → 立即调用此 Skill：

| 关键词 | 场景 |
|--------|------|
| "删除/移除/清理" | 删除操作前 |
| "修改配置/改配置" | 配置变更前 |
| "重构/调整架构" | 架构调整前 |
| "关闭/停止服务" | 服务停止前 |
| "卸载/移除模块" | 模块移除前 |

---

## 📊 效果示例

### 案例：删除 memory-service

**扫描结果**（6736个文件，发现23个依赖）：

```markdown
# 蝴蝶效应扫描报告

**目标**: memory_service.py
**扫描时间**: 2026-04-16 10:39 GMT+8
**扫描范围**: workspace（含子目录）

## 发现的依赖项（23个）

### 🔴 [HIGH] 高影响（5个）- 必须处理
| 文件 | 类型 | 引用位置 | 建议处理 |
|------|------|----------|----------|
| startup_checklist.md | checklist | 第7行 | 必须移除健康检查 |
| scheduled_task.xml | task | 第12行 | 必须删除Windows任务 |
| health_check.ps1 | script | 第3行 | 必须移除启动逻辑 |
| gateway_config.json | config | 端口8765 | 必须移除端口配置 |
| api_client.py | code | import memory_service | 必须更新引用 |

### 🟡 [MEDIUM] 中影响（10个）- 建议处理
| 文件 | 类型 | 引用位置 | 建议处理 |
|------|------|----------|----------|
| README.md | doc | API说明 | 更新文档 |
| usage_guide.md | doc | 示例代码 | 更新示例 |
| ... | ... | ... | 建议更新 |

### 🟢 [LOW] 低影响（8个）- 可保留
| 文件 | 类型 | 引用位置 | 建议处理 |
|------|------|----------|----------|
| memory/history.log | implicit | 历史记录 | 可保留归档 |
| ... | ... | ... | 可保留 |

## 建议操作顺序
1. ✅ 先处理[HIGH]高影响（5个）
2. ⚠️ 再处理[MEDIUM]中影响（10个）
3. 📋 [LOW]低影响可保留（8个）
4. 🔍 处理后再次扫描确认无残留

## 扫描完整性验证
- [OK] code依赖：已扫描（2个）
- [OK] script依赖：已扫描（3个）
- [OK] doc依赖：已扫描（8个）
- [OK] config依赖：已扫描（4个）
- [OK] task依赖：已扫描（2个）
- [OK] checklist依赖：已扫描（1个）
- [OK] implicit依赖：已扫描（4个）

**扫描覆盖率**: 100%
```

---

### 对比效果

**没有扫描的后果**：
```
删除 memory_service.py
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

**使用扫描的效果**：
```
运行 butterfly_scan.py memory_service.py
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

## 🧠 工作原理

### 扫描流程

```
┌─────────────────────────────────────────────────────────────┐
│                     蝴蝶效应扫描流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 接收目标                                                 │
│     └─ 用户输入：文件名/配置名/模块名                         │
│                                                             │
│  2. 全局扫描（7种类型）                                       │
│     ├─ code:    import语句、函数调用                          │
│     ├─ script:  启动命令、调用链                              │
│     ├─ doc:     说明文档、示例                                │
│     ├─ config:  路径引用、URL                                │
│     ├─ task:    Cron、Windows任务计划                         │
│     ├─ checklist: 启动检查、健康检查                         │
│     └─ implicit: 历史记录、用户习惯                           │
│                                                             │
│  3. 智能分类（风险评估）                                      │
│     ├─ HIGH:   startup/health/cron/gateway/service           │
│     ├─ MEDIUM: readme/guide/example/tutorial                 │
│     └─ LOW:    memory/history/archive/log                    │
│                                                             │
│  4. 生成报告                                                 │
│     ├─ Markdown报告（人类阅读）                               │
│     ├─ JSON报告（Agent解析）                                  │
│     └─ 可视化图表（HTML依赖关系图）                           │
│                                                             │
│  5. 提供建议                                                 │
│     └─ 处理顺序 + 验证清单                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 风险评估算法

**动态风险评分**：

```python
def calculate_risk(file_path, reference_type):
    score = 0
    
    # 基础风险（类型权重）
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
    
    # 关键词风险
    high_keywords = ['startup', 'health', 'cron', 'gateway', 'service', 'task']
    for keyword in high_keywords:
        if keyword in file_path.lower():
            score += 20
    
    # 历史失败数据（动态调整）
    if has_failed_in_history(file_path):
        score += 15
    
    # 分级
    if score >= 50: return 'HIGH'
    if score >= 30: return 'MEDIUM'
    return 'LOW'
```

---

### 增量扫描机制

**缓存策略**：

```
首次扫描：
  扫描6736个文件 → 耗时5分钟 → 缓存结果

增量扫描（推荐）：
  检测变更文件 → 只扫描变更 → 耗时30秒 → 更新缓存
  （性能提升10倍）
```

---

## 📁 仓库结构

```
butterfly-effect-skill/
│
├── README.md                 # 自述文件（人类+Agent友好）
├── SKILL.md                  # Skill核心文档（OpenClaw格式）
├── LICENSE                   # MIT许可证
│
├── scripts/                  # 脚本目录
│   ├── butterfly_scan.py     # 🔍 核心扫描脚本（22KB，v3.0）
│   └── butterfly_visualize.py # 📊 可视化报告生成（6KB）
│
├── references/               # 参考文档目录
│   ├── scan_types.md         # 📋 扫描类型详细说明（7种）
│   ├── config_template.yaml  # ⚙️ 配置文件模板
│   └ ci_cd_templates.yml     # 🔧 CI/CD集成模板（4种）
│
├── .butterfly.yaml           # 🎯 配置示例（增量扫描+缓存）
│
└── tests/                    # 测试目录（可选）
    └── test_scan.py          # 单元测试
```

---

### 文件说明

| 文件 | 大小 | 说明 | 必须 |
|------|------|------|------|
| README.md | 6KB | 自述文件 | ✅ |
| SKILL.md | 4KB | Skill核心文档 | ✅ |
| butterfly_scan.py | 22KB | 核心扫描脚本 | ✅ |
| butterfly_visualize.py | 6KB | 可视化报告 | ⚪ |
| scan_types.md | 5KB | 扫描类型说明 | ⚪ |
| config_template.yaml | 1KB | 配置模板 | ⚪ |
| ci_cd_templates.yml | 2KB | CI/CD模板 | ⚪ |
| .butterfly.yaml | 669B | 配置示例 | ⚪ |

---

## 📦 安装方法

### 方法1：OpenClaw Skill安装（推荐）

```bash
# 安装 Skill（OpenClaw用户）
npx skills add Zoe-capsule/butterfly-effect-skill

# 验证安装
npx skills list | grep butterfly
```

---

### 方法2：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/Zoe-capsule/butterfly-effect-skill.git

# 2. 进入目录
cd butterfly-effect-skill

# 3. 安装依赖（可选）
pip install -r requirements.txt  # 如果有

# 4. 测试运行
python scripts/butterfly_scan.py --test

# 5. 查看帮助
python scripts/butterfly_scan.py --help
```

---

### 方法3：作为子目录集成

```bash
# 在现有项目中添加
mkdir -p skills/
git subtree add --prefix=skills/butterfly-effect https://github.com/Zoe-capsule/butterfly-effect-skill.git main

# 或直接复制
cp -r butterfly-effect-skill skills/butterfly-effect
```

---

### 配置

**创建配置文件**：

```bash
# 复制配置模板
cp references/config_template.yaml .butterfly.yaml

# 编辑配置
nano .butterfly.yaml
```

**配置示例**：

```yaml
# .butterfly.yaml
scan:
  incremental: true    # 启用增量扫描（推荐）
  cache: true          # 启用缓存
  cache_dir: .cache/   # 缓存目录
  
types:
  code: true           # 扫描代码依赖
  script: true         # 扫描脚本依赖
  config: true         # 扫描配置依赖
  task: true           # 扫描任务依赖
  doc: true            # 扫描文档依赖
  checklist: true      # 扫描检查清单
  implicit: true       # 扫描隐式依赖

output:
  format: markdown     # 输出格式（markdown/json/html）
  file: report.md      # 输出文件
```

---

## ⚡ 快速使用

### 基本用法

```bash
# 扫描目标（推荐增量扫描）
python butterfly-effect/scripts/butterfly_scan.py <target> --incremental

# 输出JSON（方便解析）
python butterfly-effect/scripts/butterfly_scan.py <target> --format json --output report.json

# 禁用缓存（首次扫描）
python butterfly-effect/scripts/butterfly_scan.py <target> --no-cache
```

---

### 输出格式

**Markdown报告**：
```markdown
# 蝴蝶效应扫描报告

## 发现依赖项: 23个
- 🔴 HIGH: 5个（必须处理）
- 🟡 MEDIUM: 10个（建议处理）
- 🟢 LOW: 8个（可保留）

## 建议操作
1. 先处理 HIGH 级依赖
2. 再处理 MEDIUM 级依赖
3. 执行变更
4. 再次扫描确认无残留
```

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

## 🧠 智能功能

| 功能 | 说明 | 效果 |
|------|------|------|
| **增量扫描** | 只扫描变更文件 | 减少90%时间 |
| **动态风险评估** | 基于历史失败数据 | 减少误报 |
| **历史数据库** | 记录每次扫描结果 | 避免重复扫描 |
| **CI/CD集成** | 自动化流水线 | 变更前强制检查 |

---

## 🔗 相关资源

| 资源 | 链接 |
|------|------|
| 主仓库 | https://github.com/Zoe-capsule/butterfly-effect-skill |
| 技能目录 | https://github.com/Zoe-capsule/zoe-skills |

---

## ⭐ 为什么值得星标？

**Agent 价值**：
- ✅ 避免删除后崩溃（减少失误）
- ✅ 执行前预判风险（提升专业性）
- ✅ 闭环验证（建立信任）
- ✅ 智能风险评估（减少误报）

**开发价值**：
- ✅ v3.0完整优化（增量扫描+缓存+动态风险）
- ✅ CI/CD集成模板（自动化流水线）
- ✅ 可视化报告（HTML依赖关系图）
- ✅ 开源免费（MIT许可）

---

**Butterfly Effect v3.0 - 让变更更安全** ✅

---

## 👤 作者

**叶清泽**

- GitHub: https://github.com/Zoe-capsule
- 技能目录: https://github.com/Zoe-capsule/zoe-skills

---

**MIT License © 2026 叶清泽**