#!/usr/bin/env python3
"""
更新执行器 - 执行用户批准后的更新计划

用途：
1. 接收更新计划JSON
2. 等待用户批准（可选，如果plan中已批准）
3. 执行更新操作（edit工具）
4. 生成验证报告

版本: v1.0

红线规则：删除任何文件前必须经过用户的同意
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import shutil


# ============================================================================
# 更新执行状态
# ============================================================================

class UpdateExecutor:
    """更新执行器"""
    
    def __init__(self, plan_json_path: str):
        self.plan_path = Path(plan_json_path)
        self.plan = None
        self.results = []
        self.backup_dir = None
    
    def load_plan(self) -> Dict:
        """加载更新计划"""
        if not self.plan_path.exists():
            raise FileNotFoundError(f"计划文件不存在: {self.plan_path}")
        
        self.plan = json.loads(self.plan_path.read_text(encoding='utf-8'))
        return self.plan
    
    def create_backup(self) -> str:
        """创建备份目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.plan.get("target", "unknown")
        backup_name = f"backup_{target}_{timestamp}"
        
        # 备份目录在workspace下
        workspace = Path.home() / '.openclaw' / 'workspace'
        self.backup_dir = workspace / 'backups' / backup_name
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        return str(self.backup_dir)
    
    def backup_file(self, file_path: str) -> Optional[str]:
        """备份单个文件"""
        source = Path(file_path)
        if not source.exists():
            return None
        
        # 保持相对路径结构
        try:
            # 计算相对路径
            home = Path.home()
            if str(source).startswith(str(home)):
                rel_path = source.relative_to(home)
            else:
                rel_path = source.name
            
            backup_file = self.backup_dir / rel_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source, backup_file)
            return str(backup_file)
        except Exception as e:
            print(f"[WARN] 备份失败: {source} - {e}")
            return None
    
    def check_approval(self) -> bool:
        """检查是否已批准"""
        if self.plan.get("approved", False):
            return True
        
        # 如果没有批准，提示用户
        print("")
        print("=" * 60)
        print("⚠️ 红线规则：删除任何文件前必须经过用户的同意")
        print("=" * 60)
        print("")
        print(f"目标: {self.plan.get('target', 'unknown')}")
        print(f"HIGH影响: {self.plan.get('summary', {}).get('high', 0)} 个")
        print(f"MEDIUM影响: {self.plan.get('summary', {}).get('medium', 0)} 个")
        print("")
        
        # 显示即将执行的操作
        execution_order = self.plan.get("execution_order", [])
        print(f"即将执行 {len(execution_order)} 个更新操作：")
        print("")
        for i, update in enumerate(execution_order[:10], 1):
            print(f"{i}. [{update['impact']}] {update['action']}")
        if len(execution_order) > 10:
            print(f"... 还有 {len(execution_order) - 10} 个操作")
        print("")
        
        # 等待用户输入
        response = input("请输入 '批准' 或 'APPROVE' 继续，或 '拒绝' 取消: ").strip()
        
        if response.lower() in ['批准', 'approve', 'y', 'yes']:
            self.plan["approved"] = True
            return True
        else:
            print("[ABORT] 用户拒绝执行")
            return False
    
    def execute_update(self, update: Dict) -> Dict:
        """执行单个更新操作"""
        result = {
            "update": update,
            "status": "pending",
            "backup_path": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        file_path = Path(update.get("file", ""))
        if not file_path.exists():
            result["status"] = "skipped"
            result["error"] = "文件不存在"
            return result
        
        operation = update.get("operation", "remove_line")
        line = update.get("line", 0)
        content = update.get("content", "")
        
        # 备份文件
        if self.backup_dir:
            result["backup_path"] = self.backup_file(str(file_path))
        
        try:
            # 读取文件内容
            original_content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = original_content.split('\n')
            
            # 执行不同类型的更新
            if operation == "remove_line":
                # 删除指定行
                if 0 < line <= len(lines):
                    lines[line - 1] = ""  # 清空而不是删除（保持行号）
                    new_content = '\n'.join(lines)
                    file_path.write_text(new_content, encoding='utf-8')
                    result["status"] = "success"
                else:
                    result["status"] = "failed"
                    result["error"] = f"行号无效: {line}"
            
            elif operation == "remove_import":
                # 删除导入语句（整行）
                if 0 < line <= len(lines):
                    # 导入语句通常是完整的一行
                    del lines[line - 1]
                    new_content = '\n'.join(lines)
                    file_path.write_text(new_content, encoding='utf-8')
                    result["status"] = "success"
                else:
                    result["status"] = "failed"
                    result["error"] = f"行号无效: {line}"
            
            elif operation == "update_config":
                # 更新配置文件（需要特殊处理JSON/YAML）
                # 这里简化处理，只标记需要手动更新
                result["status"] = "manual_required"
                result["error"] = "配置文件需要手动更新（保持格式）"
            
            elif operation == "update_doc":
                # 更新文档
                if 0 < line <= len(lines):
                    # 标记需要删除的内容
                    lines[line - 1] = f"[已删除引用: {update.get('term', '')}]"
                    new_content = '\n'.join(lines)
                    file_path.write_text(new_content, encoding='utf-8')
                    result["status"] = "success"
                else:
                    result["status"] = "failed"
                    result["error"] = f"行号无效: {line}"
            
            elif operation == "modify_content":
                # 修改内容（需要手动重构）
                result["status"] = "manual_required"
                result["error"] = "需要手动重构（复杂依赖）"
            
            elif operation == "add_comment":
                # 添加注释
                if 0 < line <= len(lines):
                    comment = f"# [注意] 已移除 '{update.get('term', '')}' 相关逻辑"
                    lines.insert(line - 1, comment)
                    new_content = '\n'.join(lines)
                    file_path.write_text(new_content, encoding='utf-8')
                    result["status"] = "success"
                else:
                    result["status"] = "failed"
                    result["error"] = f"行号无效: {line}"
            
            else:
                # 默认：标记需要手动处理
                result["status"] = "manual_required"
                result["error"] = f"未知操作类型: {operation}"
        
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        return result
    
    def execute_all(self, approved: bool = False) -> List[Dict]:
        """执行所有更新"""
        if not approved:
            if not self.check_approval():
                return []
        
        # 创建备份
        backup_path = self.create_backup()
        print(f"[BACKUP] 备份目录: {backup_path}")
        
        # 执行更新
        execution_order = self.plan.get("execution_order", [])
        print(f"[START] 执行 {len(execution_order)} 个更新操作")
        
        for i, update in enumerate(execution_order, 1):
            print(f"  [{i}/{len(execution_order)}] {update['action']}")
            result = self.execute_update(update)
            self.results.append(result)
            
            if result["status"] == "success":
                print(f"    [OK] 成功")
            elif result["status"] == "manual_required":
                print(f"    [MANUAL] 需手动处理: {result['error']}")
            elif result["status"] == "skipped":
                print(f"    [SKIP] {result['error']}")
            else:
                print(f"    [FAIL] {result['error']}")
        
        return self.results
    
    def generate_report(self) -> str:
        """生成执行报告"""
        report = []
        
        report.append("# 更新执行报告")
        report.append("")
        report.append(f"**目标**: {self.plan.get('target', 'unknown')}")
        report.append(f"**执行时间**: {datetime.now().isoformat()}")
        report.append(f"**备份目录**: {self.backup_dir}")
        report.append("")
        
        # 统计
        success_count = sum(1 for r in self.results if r["status"] == "success")
        manual_count = sum(1 for r in self.results if r["status"] == "manual_required")
        failed_count = sum(1 for r in self.results if r["status"] == "failed")
        skipped_count = sum(1 for r in self.results if r["status"] == "skipped")
        total = len(self.results)
        
        report.append("## 执行统计")
        report.append("")
        report.append(f"| 状态 | 数量 | 说明 |")
        report.append(f"|------|------|------|")
        report.append(f"| 成功 | {success_count} | 已自动更新 |")
        report.append(f"| 需手动处理 | {manual_count} | 复杂依赖，需手动重构 |")
        report.append(f"| 失败 | {failed_count} | 执行出错 |")
        report.append(f"| 跳过 | {skipped_count} | 文件不存在 |")
        report.append(f"| **总计** | **{total}** | |")
        report.append("")
        
        # 详细结果
        if manual_count > 0:
            report.append("## 需手动处理的更新")
            report.append("")
            for r in self.results:
                if r["status"] == "manual_required":
                    update = r["update"]
                    report.append(f"- **{update['file']}** (Line {update['line']})")
                    report.append(f"  - 操作: {update['operation_desc']}")
                    report.append(f"  - 原因: {r['error']}")
                    report.append("")
        
        if failed_count > 0:
            report.append("## 执行失败的更新")
            report.append("")
            for r in self.results:
                if r["status"] == "failed":
                    update = r["update"]
                    report.append(f"- **{update['file']}** (Line {update['line']})")
                    report.append(f"  - 错误: {r['error']}")
                    report.append("")
        
        # 验证建议
        report.append("## 后续验证步骤")
        report.append("")
        verification_steps = self.plan.get("verification_steps", [])
        for step in verification_steps:
            report.append(step)
        report.append("")
        
        # 恢复指南
        report.append("## 如何恢复")
        report.append("")
        report.append(f"如果更新导致问题，可以从备份恢复：")
        report.append(f"```bash")
        report.append(f"# 备份位置: {self.backup_dir}")
        report.append(f"# 手动复制需要恢复的文件")
        report.append(f"```")
        report.append("")
        
        report.append("---")
        report.append(f"*更新执行器 v1.0 | 执行时间: {datetime.now().isoformat()}*")
        
        return '\n'.join(report)


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="更新执行器 - 执行用户批准后的更新计划")
    parser.add_argument("plan_json", help="更新计划JSON文件路径（由update_plan_generator.py生成）")
    parser.add_argument("--output", help="输出执行报告路径")
    parser.add_argument("--approved", action="store_true", help="跳过批准确认（已批准）")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行，不实际修改文件")
    
    args = parser.parse_args()
    
    print("[START] 更新执行器")
    print(f"  计划JSON: {args.plan_json}")
    print(f"  已批准: {args.approved}")
    print(f"  模拟执行: {args.dry_run}")
    print("")
    
    # 创建执行器
    executor = UpdateExecutor(args.plan_json)
    
    # 加载计划
    try:
        plan = executor.load_plan()
        print(f"[OK] 加载计划成功")
        print(f"  目标: {plan.get('target', 'unknown')}")
        print(f"  更新项: {len(plan.get('execution_order', []))}")
    except Exception as e:
        print(f"[ERROR] 加载计划失败: {e}")
        return
    
    # 执行
    if args.dry_run:
        print("[DRY-RUN] 模拟执行（不修改文件）")
        results = []
        for update in plan.get("execution_order", []):
            results.append({
                "update": update,
                "status": "dry_run",
                "error": None
            })
    else:
        results = executor.execute_all(approved=args.approved)
    
    # 生成报告
    if results:
        report = executor.generate_report()
        
        if args.output:
            Path(args.output).write_text(report, encoding='utf-8')
            print(f"[OK] 报告已保存: {args.output}")
        else:
            default_output = f"update_report_{plan.get('target', 'unknown')}.md"
            Path(default_output).write_text(report, encoding='utf-8')
            print(f"[OK] 报告已保存: {default_output}")
        
        print("")
        print(report)


if __name__ == "__main__":
    main()