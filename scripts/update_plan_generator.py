#!/usr/bin/env python3
"""
更新计划生成器 - 从扫描结果生成可执行的更新计划

用途：
1. 接收扫描JSON输出
2. 分析依赖影响程度
3. 生成标准化更新计划
4. 等待用户批准

版本: v1.0
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


# ============================================================================
# 更新操作类型
# ============================================================================

UPDATE_OPERATIONS = {
    "remove_line": {
        "description": "删除整行引用",
        "risk": "HIGH",
        "tool": "edit"
    },
    "remove_block": {
        "description": "删除代码块（函数/类）",
        "risk": "HIGH",
        "tool": "edit"
    },
    "modify_content": {
        "description": "修改内容（替换/重构）",
        "risk": "MEDIUM",
        "tool": "edit"
    },
    "add_comment": {
        "description": "添加注释说明",
        "risk": "LOW",
        "tool": "edit"
    },
    "update_import": {
        "description": "更新导入语句",
        "risk": "HIGH",
        "tool": "edit"
    },
    "remove_import": {
        "description": "删除导入语句",
        "risk": "HIGH",
        "tool": "edit"
    },
    "update_config": {
        "description": "更新配置文件",
        "risk": "HIGH",
        "tool": "edit"
    },
    "update_doc": {
        "description": "更新文档说明",
        "risk": "MEDIUM",
        "tool": "edit"
    }
}


# ============================================================================
# 更新计划数据结构
# ============================================================================

class UpdatePlan:
    """更新计划"""
    
    def __init__(self, target: str, scan_results: Dict):
        self.target = target
        self.scan_results = scan_results
        self.scan_time = scan_results.get("scan_time", datetime.now().isoformat())
        self.updates = []
        self.execution_order = []
        self.verification_steps = []
        self.user_approval_required = True
        self.approved = False
    
    def analyze_dependencies(self) -> List[Dict]:
        """分析依赖并生成更新项"""
        updates = []
        
        by_impact = self.scan_results.get("by_impact", {})
        
        # HIGH影响 - 必须处理
        for dep in by_impact.get("HIGH", []):
            update = self._generate_update_item(dep, "HIGH")
            if update:
                updates.append(update)
        
        # MEDIUM影响 - 建议处理
        for dep in by_impact.get("MEDIUM", []):
            update = self._generate_update_item(dep, "MEDIUM")
            if update:
                updates.append(update)
        
        # LOW影响 - 可保留（仅记录）
        for dep in by_impact.get("LOW", []):
            update = self._generate_update_item(dep, "LOW")
            if update:
                update["action"] = "保留（历史记录）"
                update["execute"] = False
                updates.append(update)
        
        return updates
    
    def _generate_update_item(self, dep: Dict, impact: str) -> Optional[Dict]:
        """为单个依赖生成更新项"""
        match_type = dep.get("match_type", "literal")
        file_path = dep.get("absolute_path", dep.get("file", ""))
        line = dep.get("line", 0)
        content = dep.get("content", "")
        term = dep.get("term", "")
        
        # 判断更新操作类型
        operation = self._determine_operation(match_type, file_path, content)
        
        # 生成具体的更新内容
        update_item = {
            "priority": 1 if impact == "HIGH" else (2 if impact == "MEDIUM" else 3),
            "impact": impact,
            "file": file_path,
            "line": line,
            "match_type": match_type,
            "content": content,
            "term": term,
            "operation": operation,
            "operation_desc": UPDATE_OPERATIONS.get(operation, {}).get("description", operation),
            "risk": UPDATE_OPERATIONS.get(operation, {}).get("risk", "MEDIUM"),
            "tool": UPDATE_OPERATIONS.get(operation, {}).get("tool", "edit"),
            "action": self._generate_action_text(operation, file_path, line, term),
            "execute": impact in ["HIGH", "MEDIUM"],  # LOW不执行
            "details": self._generate_details(match_type, file_path, line, content, term)
        }
        
        return update_item
    
    def _determine_operation(self, match_type: str, file_path: str, content: str) -> str:
        """根据匹配类型和文件类型判断操作类型"""
        # 导入语句
        if match_type in ["import", "from_import", "dynamic_import"]:
            return "remove_import"
        
        # 类继承
        if match_type == "inheritance":
            return "modify_content"  # 需要重构
        
        # 函数定义
        if match_type == "function_def":
            return "remove_block"
        
        # 配置文件
        if any(ext in file_path for ext in ['.json', '.yaml', '.yml', '.toml', '.ini']):
            return "update_config"
        
        # 文档文件
        if any(ext in file_path for ext in ['.md', '.rst', '.txt']):
            return "update_doc"
        
        # 错误消息
        if match_type == "error_msg":
            return "modify_content"
        
        # 其他
        return "remove_line"
    
    def _generate_action_text(self, operation: str, file_path: str, line: int, term: str) -> str:
        """生成具体的操作文本"""
        rel_path = file_path
        if len(rel_path) > 50:
            rel_path = "..." + rel_path[-47:]
        
        if operation == "remove_import":
            return f"删除 {rel_path} 第{line}行的导入语句"
        elif operation == "remove_line":
            return f"删除 {rel_path} 第{line}行引用"
        elif operation == "remove_block":
            return f"删除 {rel_path} 第{line}行开始的代码块"
        elif operation == "modify_content":
            return f"修改 {rel_path} 第{line}行内容（重构/替换）"
        elif operation == "update_config":
            return f"更新 {rel_path} 配置项：{term}"
        elif operation == "update_doc":
            return f"更新 {rel_path} 文档说明"
        elif operation == "add_comment":
            return f"在 {rel_path} 第{line}行添加注释"
        else:
            return f"处理 {rel_path} 第{line}行"
    
    def _generate_details(self, match_type: str, file_path: str, line: int, content: str, term: str) -> str:
        """生成详细说明"""
        details = []
        details.append(f"文件: {file_path}")
        details.append(f"行号: {line}")
        details.append(f"匹配类型: {match_type}")
        details.append(f"搜索词: {term}")
        details.append(f"内容: {content[:80]}")
        
        # 根据匹配类型添加特殊说明
        if match_type == "dynamic_import":
            details.append("⚠️ 动态导入，需检查运行时依赖")
        elif match_type == "reflection":
            details.append("⚠️ 反射调用，需检查调用链")
        elif match_type == "inheritance":
            details.append("⚠️ 类继承，需重构类结构")
        
        return '\n'.join(details)
    
    def generate_execution_order(self, updates: List[Dict]) -> List[Dict]:
        """生成执行顺序 - 按优先级和依赖关系排序"""
        # 优先级排序
        priority_order = sorted(updates, key=lambda x: (x["priority"], x["risk"]))
        
        # 同优先级内按文件路径分组（减少文件切换）
        grouped = {}
        for update in priority_order:
            file_path = update["file"]
            if file_path not in grouped:
                grouped[file_path] = []
            grouped[file_path].append(update)
        
        # 按优先级和文件分组重新排序
        execution_order = []
        for priority in [1, 2, 3]:
            for file_path, file_updates in grouped.items():
                for update in file_updates:
                    if update["priority"] == priority and update["execute"]:
                        execution_order.append(update)
        
        return execution_order
    
    def generate_verification_steps(self, target: str) -> List[str]:
        """生成验证步骤"""
        return [
            f"1. 再次扫描 '{target}' 确认无残留依赖",
            "2. 运行相关测试/启动脚本验证系统正常",
            "3. 检查日志无相关错误信息",
            "4. 用户确认功能正常"
        ]


# ============================================================================
# 生成更新计划文档
# ============================================================================

def generate_update_plan_document(plan: UpdatePlan) -> str:
    """生成标准化更新计划文档"""
    doc = []
    
    doc.append("# 更新计划")
    doc.append("")
    doc.append(f"**目标**: {plan.target}")
    doc.append(f"**扫描时间**: {plan.scan_time}")
    doc.append("")
    
    # 影响范围摘要
    summary = plan.scan_results.get("summary", {})
    doc.append("## 影响范围摘要")
    doc.append("")
    doc.append(f"| 影响等级 | 数量 | 处理建议 |")
    doc.append(f"|----------|------|----------|")
    doc.append(f"| HIGH | {summary.get('high', 0)} | 必须处理 |")
    doc.append(f"| MEDIUM | {summary.get('medium', 0)} | 建议处理 |")
    doc.append(f"| LOW | {summary.get('low', 0)} | 可保留 |")
    doc.append(f"| **总计** | **{summary.get('total', 0)}** | |")
    doc.append("")
    
    # 生成更新项
    updates = plan.analyze_dependencies()
    plan.updates = updates
    
    doc.append("## 需要更新的依赖")
    doc.append("")
    
    # HIGH影响
    high_updates = [u for u in updates if u["impact"] == "HIGH" and u["execute"]]
    if high_updates:
        doc.append(f"### 🔴 HIGH影响（{len(high_updates)}个）- 必须处理")
        doc.append("")
        doc.append("| 优先级 | 文件 | 更新内容 | 风险等级 |")
        doc.append("|--------|------|----------|----------|")
        for u in high_updates:
            rel_path = u["file"]
            if len(rel_path) > 50:
                rel_path = "..." + rel_path[-47:]
            doc.append(f"| {u['priority']} | {rel_path} | {u['action']} | {u['risk']} |")
        doc.append("")
    
    # MEDIUM影响
    medium_updates = [u for u in updates if u["impact"] == "MEDIUM" and u["execute"]]
    if medium_updates:
        doc.append(f"### 🟡 MEDIUM影响（{len(medium_updates)}个）- 建议处理")
        doc.append("")
        doc.append("| 优先级 | 文件 | 更新内容 | 风险等级 |")
        doc.append("|--------|------|----------|----------|")
        for u in medium_updates[:20]:  # 最多显示20个
            rel_path = u["file"]
            if len(rel_path) > 50:
                rel_path = "..." + rel_path[-47:]
            doc.append(f"| {u['priority']} | {rel_path} | {u['action']} | {u['risk']} |")
        if len(medium_updates) > 20:
            doc.append(f"| ... | ... | ... | 还有{len(medium_updates) - 20}个 |")
        doc.append("")
    
    # LOW影响（可保留）
    low_updates = [u for u in updates if u["impact"] == "LOW"]
    if low_updates:
        doc.append(f"### 🟢 LOW影响（{len(low_updates)}个）- 可保留")
        doc.append("")
        doc.append("- 历史记录/日志输出，不影响系统运行")
        doc.append("")
    
    # 执行顺序
    execution_order = plan.generate_execution_order(updates)
    plan.execution_order = execution_order
    
    doc.append("## 执行顺序")
    doc.append("")
    doc.append("**推荐执行顺序**：")
    doc.append("")
    
    if execution_order:
        for i, update in enumerate(execution_order, 1):
            rel_path = update["file"]
            if len(rel_path) > 50:
                rel_path = "..." + rel_path[-47:]
            doc.append(f"{i}. [{update['impact']}] {update['action']}")
    else:
        doc.append("**无需要执行的更新项**")
    
    doc.append("")
    
    # 验证步骤
    verification_steps = plan.generate_verification_steps(plan.target)
    plan.verification_steps = verification_steps
    
    doc.append("## 验证步骤")
    doc.append("")
    for step in verification_steps:
        doc.append(step)
    doc.append("")
    
    # 用户批准请求
    doc.append("## 请用户批准后执行")
    doc.append("")
    doc.append("**红线规则#4**: 删除任何文件前必须经过用户的同意")
    doc.append("")
    doc.append("请回复：")
    doc.append("- `批准` 或 `APPROVE` → 执行所有HIGH和MEDIUM更新")
    doc.append("- `批准HIGH` → 仅执行HIGH影响更新")
    doc.append("- `拒绝` 或 `REJECT` → 不执行任何更新")
    doc.append("- `自定义` → 指定特定文件更新")
    doc.append("")
    doc.append("---")
    doc.append(f"*更新计划生成器 v1.0 | 生成时间: {datetime.now().isoformat()}*")
    
    return '\n'.join(doc)


def generate_json_plan(plan: UpdatePlan) -> Dict:
    """生成JSON格式的更新计划（用于update_executor）"""
    updates = plan.analyze_dependencies()
    execution_order = plan.generate_execution_order(updates)
    
    return {
        "target": plan.target,
        "scan_time": plan.scan_time,
        "summary": plan.scan_results.get("summary", {}),
        "updates": updates,
        "execution_order": execution_order,
        "verification_steps": plan.generate_verification_steps(plan.target),
        "approval_required": True,
        "approved": False
    }


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="更新计划生成器 - 从扫描结果生成可执行的更新计划")
    parser.add_argument("scan_json", help="扫描JSON文件路径（由butterfly_scan_v3.5.py生成）")
    parser.add_argument("--output", help="输出更新计划文档路径")
    parser.add_argument("--json", help="输出JSON格式更新计划（用于update_executor）")
    
    args = parser.parse_args()
    
    # 读取扫描结果
    scan_file = Path(args.scan_json)
    if not scan_file.exists():
        print(f"[ERROR] 扫描JSON文件不存在: {scan_file}")
        return
    
    try:
        scan_data = json.loads(scan_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON解析失败: {e}")
        return
    
    target = scan_data.get("target", "unknown")
    
    print(f"[START] 更新计划生成器")
    print(f"  目标: {target}")
    print(f"  扫描JSON: {scan_file}")
    print("")
    
    # 创建更新计划
    plan = UpdatePlan(target, scan_data)
    
    # 生成文档
    document = generate_update_plan_document(plan)
    
    # 保存文档
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(document, encoding='utf-8')
        print(f"[OK] 更新计划已保存: {output_path}")
    else:
        default_output = f"update_plan_{target}.md"
        Path(default_output).write_text(document, encoding='utf-8')
        print(f"[OK] 更新计划已保存: {default_output}")
    
    # JSON输出
    if args.json:
        json_plan = generate_json_plan(plan)
        json_path = Path(args.json)
        json_path.write_text(json.dumps(json_plan, indent=2), encoding='utf-8')
        print(f"[OK] JSON计划已保存: {json_path}（可用于update_executor）")
    
    # 打印摘要
    summary = scan_data.get("summary", {})
    print("")
    print("[SUMMARY]")
    print(f"  HIGH影响: {summary.get('high', 0)} 个（必须处理）")
    print(f"  MEDIUM影响: {summary.get('medium', 0)} 个（建议处理）")
    print(f"  LOW影响: {summary.get('low', 0)} 个（可保留）")
    print(f"  总计: {summary.get('total', 0)} 个")
    print("")
    print("请用户批准后执行更新")


if __name__ == "__main__":
    main()