---
name: butterfly-effect
author: Zoe-capsule
author_github: Zoe-capsule
version: 3.5
description: 全局依赖扫描+同步更新器，在局部增删改前预判影响范围并执行同步更新，避免隐性错误和BUG。**v3.5重大升级**：完整更新闭环（扫描→生成计划→用户批准→执行更新→验证）+ AST深度解析（检测动态导入、反射调用、类继承）+ 智能过滤（HIGH优先显示，MEDIUM/LOW折叠）+ 通用路径支持（自动检测用户目录）。**v3.4新增增强扫描**：8种匹配类型。**v3.3新增三层扫描机制**：配置文件层+Workspace层+系统代码层。触发场景：(1) 用户要求删除文件 (2) 用户要求修改配置 (3) 用户要求调整架构 (4) 用户要求移除服务/模块 (5) 用户要求修改脚本。包含7种扫描类型，分类影响程度（高/中/低），生成更新计划并执行同步更新。
---

# 蝴蝶效应扫描器

全局依赖扫描，防止遗漏隐藏依赖导致系统性故障。

---

## 核心功能

**一句话**: 执行任何变更操作前，先全局扫描所有可能依赖。

**防止的问题**:
- 删除文件后，启动脚本失败
- 配置变更后，健康检查失败
- 架构调整后，模块耦合失效

---

## v3.5重大升级（P1+P2优化）

### 完整更新闭环
三个脚本实现完整流程：

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| **butterfly_scan_v3.5.py** | AST+正则扫描 | 目标关键词 | JSON扫描结果 |
| **update_plan_generator.py** | 生成更新计划 | 扫描JSON | 更新计划文档+JSON |
| **update_executor.py** | 执行更新操作 | 计划JSON | 执行报告 |

### AST深度解析（Python）
检测复杂依赖，原版正则无法识别：

| AST检测类型 | 说明 | 影响程度 |
|-------------|------|----------|
| **dynamic_import** | `__import__('xxx')`, `importlib.import_module()` | HIGH |
| **reflection** | `getattr(obj, 'attr')` 反射调用 | HIGH |
| **inheritance** | `class Foo(Base)` 类继承 | HIGH |
| **import/from_import** | 静态导入语句 | HIGH |
| **attribute_access** | 属性访问 `obj.attr` | MEDIUM |
| **function_def** | 函数定义包含关键词 | MEDIUM |

### 智能过滤
HIGH优先显示，MEDIUM/LOW折叠，避免信息过载：

```
HIGH: 14个 → 全部显示（必须处理）
MEDIUM: 45个 → 显示3个样本（建议处理，--show-all查看全部）
LOW: 50个 → 显示3个样本（可保留，历史记录）
```

### 通用路径支持
自动检测用户目录，不硬编码：

```python
def get_user_home(): Path(os.path.expanduser('~'))
def get_openclaw_root(): Path.home() / '.openclaw'
def get_openclaw_system_path(): # 自动检测npm全局安装路径
```

---

## 增强扫描模式（v3.4）

基于用户反馈，新增8种匹配类型，解决原版遗漏风险：

| 匹配类型 | 遗漏风险 | 说明 |
|----------|----------|------|
| **literal** | - | 字面字符串匹配（原版） |
| **dynamic_path** | HIGH | 动态路径拼接（f-string, os.path.join） |
| **conditional** | HIGH | 条件分支引用（if/else if/elif） |
| **method_call** | HIGH | 方法调用（.get/.post/.fetch） |
| **env_var** | HIGH | 环境变量依赖（os.environ） |
| **error_msg** | MEDIUM | 错误消息（raise/throw/Error） |
| **log_output** | LOW | 日志输出（print/console.log） |
| **docstring** | LOW | 文档字符串（TODO/FIXME） |

---

基于实际使用反馈，扫描范围扩展为三层，避免遗漏配置文件和系统代码依赖：

| 层级 | 路径 | 扫描内容 |
|------|------|----------|
| **配置文件层** | `~/.openclaw/` | Gateway配置、模型配置、凭证、cron任务 |
| **Workspace层** | `~/.openclaw/workspace/` | 用户文件、skills、scripts、docs、plugins |
| **系统代码层** | `npm/node_modules/openclaw/dist/` | OpenClaw核心代码、内置扩展、control-ui |

**优势**：
- 配置变更时扫描Gateway配置文件
- 删除文件时扫描所有用户代码
- 移除服务时扫描系统内置依赖

---

## 扫描类型（7种）

| 类型 | 文件扩展名 | 说明 |
|------|------------|------|
| **code** | .py, .js, .ts, .go, .java | 代码依赖（import、函数调用） |
| **script** | .ps1, .bat, .sh, .cmd | 脚本依赖（启动命令、调用链） |
| **doc** | .md, .rst, .txt | 文档依赖（说明文档、示例） |
| **config** | .json, .yaml, .xml, .toml | 配置依赖（路径引用、URL） |
| **task** | .xml, cron配置 | 任务依赖（Cron、Windows任务计划） |
| **checklist** | checklist.md | 检查清单（启动检查、健康检查） |
| **implicit** | memory/, logs/ | 隐式依赖（历史记录、用户习惯） |

---

## 使用流程（完整执行闭环）

**用户确认的流程**：
```
局部增删改 → 扫描影响 → 生成更新计划 → 叶哥批准 → 执行同步更新 → 验证
```

### 详细步骤

**Step 1: 接收目标**
- 触发场景：用户要求删除文件、修改配置、调整架构

**Step 2: 扫描影响**
- 运行增强版扫描脚本（推荐）：scripts/butterfly_scan_enhanced.py
- 运行三层扫描脚本：scripts/butterfly_scan_layers.py
- 或运行单层扫描脚本：scripts/butterfly_scan.py
- 分析扫描结果（按匹配类型分类：literal/dynamic_path/conditional/method_call/env_var/error_msg/log_output/docstring）
- 分析扫描结果（按影响程度分类：HIGH/MEDIUM/LOW）

**Step 3: 生成更新计划**
- **不是报告，而是可执行计划**
- 列出需要更新的文件、更新内容、执行顺序

**Step 4: 用户批准**
- 红线规则#4：删除任何文件前必须经过用户的同意
- 展示更新计划，等待批准

**Step 5: 执行同步更新**
- 使用 read/edit/exec 工具
- 按更新计划逐一执行

**Step 6: 验证**
- 再次扫描确认无残留依赖
- 测试系统正常运行

---

### 更新计划格式（标准化）

```markdown
# 更新计划

**目标**: <目标文件>
**影响范围**: <扫描结果摘要>

## 需要更新的依赖（X个）

| 优先级 | 文件 | 更新内容 | 风险等级 |
|--------|------|----------|----------|
| 1 | startup.ps1 | 删除第15行引用 | HIGH |
| 2 | config.json | 删除service_name字段 | MEDIUM |
| 3 | README.md | 删除说明段落 | LOW |

## 执行顺序
1. 先处理HIGH（必须）
2. 再处理MEDIUM（推荐）
3. LOW可保留

## 预期结果
- 删除X个引用
- 无残留依赖
- 系统正常运行

## 请用户批准后执行
```

---

## 扫描命令

### v3.5完整流程（推荐）
```bash
# Step 1: 扫描（AST+正则+智能过滤）
python scripts/butterfly_scan_v3.5.py <target> --json scan_result.json

# Step 2: 生成更新计划
python scripts/update_plan_generator.py scan_result.json --json update_plan.json

# Step 3: 执行更新（需用户批准）
python scripts/update_executor.py update_plan.json --output report.md
```

### 基本用法（单层扫描）
```bash
python scripts/butterfly_scan.py <target> --workspace <path>
```

### 分层扫描（v3.0新增）
```bash
# 快速层（30秒，适合其他Agent）
python scripts/butterfly_scan.py <target> --layer quick

# 标准层（60秒，启用历史数据库）
python scripts/butterfly_scan.py <target> --layer standard

# 完整层（5分钟，默认，完整分析）
python scripts/butterfly_scan.py <target> --layer full
```

### 轻量扫描器（其他Agent推荐）
```bash
# 30秒完成，适合快速预判
python scripts/butterfly_quick_scan.py <target> --workspace <path> --output json
```

### 指定搜索词
```bash
python scripts/butterfly_scan.py example_service.py --terms "service_name" "8765" "my_service"
```

### 保存报告
```bash
python scripts/butterfly_scan.py <target> --output butterfly_report.md
```

---

## 输出格式

### 标准化报告结构
```markdown
# 蝴蝶效应扫描报告

**目标**: <目标文件>
**扫描时间**: <时间戳>
**扫描范围**: workspace（含子目录）

## 发现的依赖项（X个）

### [HIGH] 高影响（X个）
| 文件 | 类型 | 引用位置 | 建议处理 |
|------|------|----------|----------|
| ... | ... | ... | 必须处理 |

### [MEDIUM] 中影响（X个）
...

### [LOW] 低影响（X个）
...

## 建议操作顺序
1. 先处理[HIGH]高影响
2. 再处理[MEDIUM]中影响
3. [LOW]低影响可保留
4. 处理后再次扫描确认

## 扫描完整性验证
- [OK] code依赖：已扫描
- [OK] script依赖：已扫描
- ...（7种全部验证）

**扫描覆盖率**: 100%
```

---

## 影响程度判定

| 等级 | 关键词 | 处理建议 |
|------|--------|----------|
| **HIGH** | startup, health, cron, task, gateway, service | 必须处理，否则系统失败 |
| **MEDIUM** | readme, guide, example, tutorial | 建议处理，避免用户困惑 |
| **LOW** | memory, history, archive, log | 可保留，作为历史记录 |

---

## 红线规则

**执行前强制扫描**:
- 禁止声称"无影响"前完成扫描
- 禁止只看代码不看文档/任务计划
- 禁止遗漏检查清单类型

**扫描完整性验证**:
- 必须列出所有可能的引用类型
- 必须验证扫描覆盖率100%
- 必须分类影响程度并提供处理建议

---

## 实际价值（已验证）

**案例**: 删除`example_service.py`

| 发现的依赖 | 影响程度 | 处理结果 |
|------------|----------|----------|
| startup_checklist.md | HIGH | 已移除健康检查 |
| scheduled_task.xml | HIGH | 已删除Windows任务 |
| health_check.ps1 | HIGH | 已移除启动逻辑 |
| README_service_setup.md | MEDIUM | 已删除失效文档 |

**避免的故障**: 3个严重故障点（启动失败、任务失败、文档不一致）

---

## 详细参考

扫描类型详细说明见: [references/scan_types.md](references/scan_types.md)

---

## 与系统配置的关系

- **系统配置**: 理论指导（流程、红线规则）
- **本Skill**: 工具化执行（自动化扫描、标准化报告）

**互补关系**:
1. 系统配置提供思维框架
2. Skill提供工具支持
3. 两者结合 = 完整的蝴蝶效应执行体系

---

## 版本信息

- **版本**: v3.5
- **更新时间**: 2026-04-18
- **更新内容**: P1+P2优化：完整更新闭环 + AST深度解析 + 智能过滤 + 通用路径支持
- **新增脚本**: butterfly_scan_v3.5.py, update_plan_generator.py, update_executor.py
- **验证状态**: 功能实现完成，待实际案例验证
- **最终目标**: 提前想到局部增删改的影响并执行同步更新，避免隐性错误和BUG