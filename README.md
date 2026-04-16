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

## 📦 安装

```bash
# 安装 Skill
npx skills add Zoe-capsule/butterfly-effect-skill

# 或手动安装
git clone https://github.com/Zoe-capsule/butterfly-effect-skill.git
```

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