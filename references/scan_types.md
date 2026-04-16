# 扫描类型详细说明

本文档详细说明蝴蝶效应扫描器的7种扫描类型及其使用场景。

---

## 1. 代码依赖（Code Dependencies）

### 扫描目标
- `.py` - Python脚本
- `.js`, `.ts` - JavaScript/TypeScript
- `.go` - Go语言
- `.java` - Java
- `.cpp`, `.c` - C/C++

### 检查内容
- **直接引用**: import语句、require语句
- **函数调用**: 函数名匹配
- **路径引用**: 文件路径字符串
- **API调用**: URL或endpoint引用

### 示例匹配
```python
# Python import
from scripts.example_service import start_service

# 函数调用
result = example_service.health_check()

# 路径引用
config_path = "scripts/example_service.py"
```

---

## 2. 脚本依赖（Script Dependencies）

### 扫描目标
- `.ps1` - PowerShell脚本
- `.bat`, `.cmd` - Windows批处理
- `.sh` - Shell脚本
- `.vbs` - VBScript

### 检查内容
- **启动命令**: Start-Process、python命令
- **参数传递**: -ArgumentList参数
- **路径引用**: 脚本文件路径
- **调用链**: 多脚本互相调用

### 示例匹配
```powershell
# PowerShell启动命令
Start-Process python.exe -ArgumentList "example_service.py"

# 批处理调用
call start_service.bat
```

---

## 3. 文档依赖（Documentation Dependencies）

### 扫描目标
- `.md` - Markdown文档
- `.rst` - reStructuredText
- `.txt` - 纯文本
- `.docx` - Word文档（需特殊处理）

### 检查内容
- **说明文档**: README、使用指南
- **示例引用**: 代码示例中的文件名
- **路径说明**: 文档中的路径说明
- **教程引用**: 教程步骤中的引用

### 示例匹配
```markdown
# README.md
启动命令: python example_service.py

# 使用指南
参见 scripts/example_service.py 实现细节
```

---

## 4. 配置依赖（Configuration Dependencies）

### 扫描目标
- `.json` - JSON配置
- `.yaml`, `.yml` - YAML配置
- `.xml` - XML配置
- `.toml` - TOML配置
- `.ini` - INI配置

### 检查内容
- **路径引用**: config中的文件路径
- **URL引用**: baseUrl、endpoint配置
- **端口引用**: localhost:8765等
- **服务引用**: service名称配置

### 示例匹配
```json
{
  "service": {
    "baseUrl": "http://localhost:8765"
  }
}
```

```yaml
service:
  name: example_service
  port: 8765
```

---

## 5. 任务依赖（Task Dependencies）

### 扫描目标
- `.xml` - Windows任务计划XML
- `.cron` - Cron配置（虚拟扩展名）
- 特殊路径: `cron`, `task-scheduler`

### 检查内容
- **Cron任务**: 定时任务配置
- **Windows任务**: Task Scheduler XML
- **触发条件**: 任务触发器配置
- **执行命令**: 任务执行的命令

### 示例匹配
```xml
<!-- Windows Task Scheduler -->
<Command>python.exe</Command>
<Arguments>example_service.py</Arguments>
```

```cron
# Cron配置
0 9 * * * python /path/to/example_service.py
```

---

## 6. 检查清单（Checklist Dependencies）

### 扫描目标
- `.md` - Markdown检查清单
- 特殊模式: `checklist`, `startup`, `health`

### 检查内容
- **启动检查**: startup-checklist.md
- **健康检查**: health-check步骤
- **验证步骤**: 验证流程中的引用
- **必做步骤**: 检查清单中的必做项

### 示例匹配
```markdown
# startup-checklist.md
- [ ] 服务健康检查: http://localhost:8765/health

# health-check.ps1
Invoke-RestMethod -Uri "http://localhost:8765/health"
```

---

## 7. 隐式依赖（Implicit Dependencies）

### 扫描目标
- `.md`, `.log`, `.txt` - 历史记录文件
- 特殊路径: `logs`, `history`

### 检查内容
- **用户习惯**: 用户常用的操作路径
- **历史记录**: logs文件中的历史引用
- **日志文件**: 错误日志中的引用
- **外部调用**: 第三方工具的调用记录

### 示例匹配
```markdown
# logs/2024-03-30.md
启动服务: example_service.py

# logs/error.log
[ERROR] example_service.py failed to start
```

---

## 影响程度判定规则

### HIGH（高影响）
包含以下关键词的依赖：
- `startup` - 启动相关
- `health` - 健康检查
- `cron` - 定时任务
- `task` - 任务计划
- `gateway` - Gateway配置
- `service` - 服务配置

**处理建议**: 必须处理，否则系统会失败

---

### MEDIUM（中影响）
包含以下关键词的依赖：
- `readme` - 说明文档
- `guide` - 使用指南
- `example` - 示例文档
- `tutorial` - 教程文档

**处理建议**: 建议处理，避免用户困惑

---

### LOW（低影响）
包含以下关键词的依赖：
- `memory` - 历史记忆
- `history` - 历史记录
- `archive` - 归档文件
- `log` - 日志文件

**处理建议**: 可保留，作为历史记录

---

## 扫描覆盖率验证

每次扫描后，验证以下类型是否全部扫描：

```
[OK] code依赖 - 已扫描
[OK] script依赖 - 已扫描
[OK] doc依赖 - 已扫描
[OK] config依赖 - 已扫描
[OK] task依赖 - 已扫描
[OK] checklist依赖 - 已扫描
[OK] implicit依赖 - 已扫描

覆盖率: 100%
```

---

## 实际案例参考

### 案例: example_service.py删除

**发现的依赖**:
| 文件 | 类型 | 影响程度 |
|------|------|----------|
| startup_checklist.md | checklist | HIGH |
| scheduled_task.xml | task | HIGH |
| health_check.ps1 | script | HIGH |
| README_service_setup.md | doc | MEDIUM |

**处理结果**: 全部处理，避免3个严重故障

---

## 版本历史

- v1.0: 初始版本，7种扫描类型定义