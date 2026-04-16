#!/usr/bin/env python3
"""
蝴蝶效应扫描器 v3.0 - 全局依赖扫描脚本（完整优化版）
新增功能：
  - v1.0: 基础扫描
  - v2.0: 增量扫描 + 缓存 + JSON输出 + 验证
  - v3.0: 配置文件支持 + 历史数据库 + 动态风险评估 + CI/CD模板
"""

import os
import re
import json
import yaml
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import hashlib

class ConfigManager:
    """配置管理器 - 读取.butterfly.yaml配置文件"""
    
    CONFIG_FILE = ".butterfly.yaml"
    
    DEFAULT_CONFIG = {
        "scan": {
            "mode": "full",
            "use_cache": True,
            "cache_file": ".butterfly_cache.json",
            "exclude_paths": [".git", ".bak", "node_modules", "__pycache__", "dist", "build"]
        },
        "scan_types": {
            "code": {"extensions": ["py", "js", "ts", "go", "java", "cpp", "c"], "enabled": True},
            "script": {"extensions": ["ps1", "bat", "sh", "cmd", "vbs"], "enabled": True},
            "doc": {"extensions": ["md", "rst", "txt", "docx"], "enabled": True},
            "config": {"extensions": ["json", "yaml", "yml", "xml", "toml", "ini"], "enabled": True},
            "task": {"extensions": ["xml", "cron"], "enabled": True},
            "checklist": {"extensions": ["md"], "patterns": ["checklist", "startup", "health"], "enabled": True},
            "implicit": {"extensions": ["md", "log", "txt"], "patterns": ["memory", "log", "history"], "enabled": True}
        },
        "impact_rules": {
            "high": {"keywords": ["startup", "health", "cron", "task", "gateway", "service"], "action": "必须处理"},
            "medium": {"keywords": ["readme", "guide", "example", "tutorial"], "action": "建议处理"},
            "low": {"keywords": ["memory", "history", "archive", "log"], "action": "可保留"}
        },
        "output": {
            "format": "markdown",
            "path": "butterfly_report.md",
            "include_performance": True,
            "include_coverage": True
        },
        "history": {
            "enabled": True,
            "db_path": ".butterfly_history.json",
            "max_records": 100
        },
        "dynamic_risk": {
            "enabled": True,
            "failure_thresholds": {"high": 5, "medium": 3}
        }
    }
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.config_path = self.workspace / self.CONFIG_FILE
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                # 合并默认配置
                return self._merge_config(self.DEFAULT_CONFIG, user_config)
            except Exception as e:
                print(f"[WARN] 配置文件加载失败，使用默认配置: {e}")
                return self.DEFAULT_CONFIG
        return self.DEFAULT_CONFIG
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default=None) -> any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value


class HistoryManager:
    """历史管理器 - 记录扫描历史和变更影响"""
    
    def __init__(self, workspace_path: str, config: ConfigManager):
        self.workspace = Path(workspace_path)
        self.config = config
        self.history_path = self.workspace / config.get("history.db_path", ".butterfly_history.json")
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """加载历史记录"""
        if self.history_path.exists():
            try:
                return json.loads(self.history_path.read_text(encoding='utf-8'))
            except:
                return {"version": "3.0", "records": [], "file_failures": {}}
        return {"version": "3.0", "records": [], "file_failures": {}}
    
    def _save_history(self) -> None:
        """保存历史记录"""
        max_records = self.config.get("history.max_records", 100)
        # 保留最近N条记录
        if len(self.history["records"]) > max_records:
            self.history["records"] = self.history["records"][-max_records:]
        
        self.history_path.write_text(
            json.dumps(self.history, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def add_scan_record(self, report: Dict) -> None:
        """添加扫描记录"""
        record = {
            "target": report.get("target"),
            "scan_time": report.get("scan_time"),
            "total_deps": len(report.get("dependencies", [])),
            "high_count": len([d for d in report.get("dependencies", []) if d.get("impact") == "high"]),
            "scan_mode": report.get("performance", {}).get("scan_mode", "full")
        }
        self.history["records"].append(record)
        self._save_history()
    
    def record_failure(self, file_path: str) -> None:
        """记录文件失败历史"""
        if file_path not in self.history["file_failures"]:
            self.history["file_failures"][file_path] = {"count": 0, "last_failure": None}
        
        self.history["file_failures"][file_path]["count"] += 1
        self.history["file_failures"][file_path]["last_failure"] = datetime.now().isoformat()
        self._save_history()
    
    def get_failure_count(self, file_path: str) -> int:
        """获取文件失败次数"""
        if file_path in self.history["file_failures"]:
            return self.history["file_failures"][file_path]["count"]
        return 0
    
    def get_recent_failures(self, limit: int = 10) -> List[Dict]:
        """获取最近失败记录"""
        failures = []
        for file_path, data in self.history["file_failures"].items():
            failures.append({
                "file": file_path,
                "count": data["count"],
                "last_failure": data["last_failure"]
            })
        # 按失败次数排序
        failures.sort(key=lambda x: x["count"], reverse=True)
        return failures[:limit]


class DynamicRiskEvaluator:
    """动态风险评估器 - 基于历史数据调整风险等级"""
    
    def __init__(self, history: HistoryManager, config: ConfigManager):
        self.history = history
        self.config = config
    
    def evaluate_risk(self, dep: Dict) -> str:
        """动态评估风险等级"""
        base_impact = dep.get("impact", "medium")
        file_path = dep.get("file", "")
        
        # 如果动态风险评估未启用，返回基础风险
        if not self.config.get("dynamic_risk.enabled", True):
            return base_impact
        
        # 获取失败次数
        failure_count = self.history.get_failure_count(file_path)
        
        # 根据失败次数调整风险
        thresholds = self.config.get("dynamic_risk.failure_thresholds", {"high": 5, "medium": 3})
        high_threshold = thresholds.get("high", 5)
        medium_threshold = thresholds.get("medium", 3)
        
        if failure_count >= high_threshold:
            return "high"
        elif failure_count >= medium_threshold:
            if base_impact == "low":
                return "medium"
        
        return base_impact
    
    def get_risk_reason(self, dep: Dict) -> str:
        """获取风险等级原因"""
        file_path = dep.get("file", "")
        failure_count = self.history.get_failure_count(file_path)
        
        if failure_count > 0:
            return f"历史失败{failure_count}次"
        return "静态分析"


class CacheManager:
    """缓存管理器 - 存储上次扫描结果"""
    
    def __init__(self, workspace_path: str, config: ConfigManager):
        self.workspace = Path(workspace_path)
        self.config = config
        self.cache_path = self.workspace / config.get("scan.cache_file", ".butterfly_cache.json")
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """加载缓存"""
        if self.cache_path.exists():
            try:
                return json.loads(self.cache_path.read_text(encoding='utf-8'))
            except:
                return {"version": "3.0", "scans": {}}
        return {"version": "3.0", "scans": {}}
    
    def _save_cache(self) -> None:
        """保存缓存"""
        self.cache_path.write_text(
            json.dumps(self.cache, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def get_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        try:
            content = file_path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except:
            return ""
    
    def is_file_changed(self, file_path: Path) -> bool:
        """检查文件是否变更"""
        relative_path = str(file_path.relative_to(self.workspace))
        current_hash = self.get_file_hash(file_path)
        
        if relative_path in self.cache["scans"]:
            cached_hash = self.cache["scans"][relative_path].get("hash", "")
            return current_hash != cached_hash
        
        return True
    
    def update_file_cache(self, file_path: Path, dependencies: List[Dict]) -> None:
        """更新文件缓存"""
        relative_path = str(file_path.relative_to(self.workspace))
        current_hash = self.get_file_hash(file_path)
        
        self.cache["scans"][relative_path] = {
            "hash": current_hash,
            "dependencies": dependencies,
            "scan_time": datetime.now().isoformat()
        }
        
        self._save_cache()
    
    def get_cached_dependencies(self, file_path: Path) -> Optional[List[Dict]]:
        """获取缓存的依赖项"""
        relative_path = str(file_path.relative_to(self.workspace))
        
        if relative_path in self.cache["scans"]:
            if not self.is_file_changed(file_path):
                return self.cache["scans"][relative_path].get("dependencies", [])
        
        return None


class GitDiffScanner:
    """Git差异扫描器"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
    
    def get_changed_files(self, since_commit: str = "HEAD~1") -> List[Path]:
        """获取最近变更的文件"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", since_commit],
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                changed_files = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        file_path = self.workspace / line
                        if file_path.exists():
                            changed_files.append(file_path)
                return changed_files
            return []
        except:
            return []
    
    def is_git_available(self) -> bool:
        """检查Git是否可用"""
        try:
            result = subprocess.run(
                ["git", "status"],
                cwd=str(self.workspace),
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


class ButterflyScanner:
    """蝴蝶效应扫描器 v3.0（完整优化版）"""
    
    def __init__(self, workspace_path: str, config_path: Optional[str] = None):
        self.workspace = Path(workspace_path)
        self.config = ConfigManager(workspace_path)
        self.history = HistoryManager(workspace_path, self.config)
        self.dynamic_risk = DynamicRiskEvaluator(self.history, self.config)
        self.cache = CacheManager(workspace_path, self.config) if self.config.get("scan.use_cache", True) else None
        self.git_scanner = GitDiffScanner(workspace_path)
        
        self.results = {
            "target": None,
            "scan_time": None,
            "dependencies": [],
            "scan_coverage": {},
            "performance": {
                "total_files": 0,
                "cached_files": 0,
                "scanned_files": 0,
                "scan_duration_ms": 0
            },
            "dynamic_risks": []
        }
    
    def scan(self, target: str, search_terms: List[str], incremental: bool = False) -> Dict:
        """执行扫描"""
        start_time = datetime.now()
        
        self.results["target"] = target
        self.results["scan_time"] = datetime.now().isoformat()
        
        # 获取扫描文件列表
        scan_mode = self.config.get("scan.mode", "full")
        if incremental or scan_mode == "incremental":
            if self.git_scanner.is_git_available():
                scan_files = self.git_scanner.get_changed_files()
                self.results["performance"]["scan_mode"] = "incremental"
            else:
                scan_files = self._get_all_files()
                self.results["performance"]["scan_mode"] = "full_fallback"
        else:
            scan_files = self._get_all_files()
            self.results["performance"]["scan_mode"] = "full"
        
        self.results["performance"]["total_files"] = len(scan_files)
        
        # 扫描各类型
        scan_types = self.config.get("scan_types", {})
        for scan_type, type_config in scan_types.items():
            if type_config.get("enabled", True):
                found_deps = self._scan_type(scan_type, type_config, search_terms, scan_files)
                self.results["dependencies"].extend(found_deps)
                self.results["scan_coverage"][scan_type] = len(found_deps) > 0
        
        # 动态风险评估
        self._apply_dynamic_risk()
        
        # 记录性能
        end_time = datetime.now()
        self.results["performance"]["scan_duration_ms"] = int((end_time - start_time).total_seconds() * 1000)
        
        # 记录历史
        self.history.add_scan_record(self.results)
        
        return self.results
    
    def _get_all_files(self) -> List[Path]:
        """获取所有可扫描文件"""
        all_files = []
        exclude_paths = self.config.get("scan.exclude_paths", [])
        
        scan_types = self.config.get("scan_types", {})
        for scan_type, type_config in scan_types.items():
            if type_config.get("enabled", True):
                extensions = type_config.get("extensions", [])
                for ext in extensions:
                    for file_path in self.workspace.rglob(f"*.{ext}"):
                        # 检查排除路径
                        should_exclude = any(ex in str(file_path) for ex in exclude_paths)
                        if not should_exclude:
                            all_files.append(file_path)
        
        return all_files
    
    def _scan_type(self, scan_type: str, config: Dict, search_terms: List[str], scan_files: List[Path]) -> List[Dict]:
        """扫描特定类型"""
        dependencies = []
        
        extensions = config.get("extensions", [])
        matching_files = [f for f in scan_files if any(f.suffix.lstrip('.') == ext for ext in extensions)]
        
        for file_path in matching_files:
            # 使用缓存
            if self.cache:
                cached_deps = self.cache.get_cached_dependencies(file_path)
                if cached_deps is not None:
                    dependencies.extend(cached_deps)
                    self.results["performance"]["cached_files"] += 1
                    continue
            
            self.results["performance"]["scanned_files"] += 1
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for term in search_terms:
                    if term.lower() in content.lower():
                        matches = self._find_matches(content, term)
                        
                        for match in matches:
                            dep = {
                                "file": str(file_path.relative_to(self.workspace)),
                                "type": scan_type,
                                "term": term,
                                "line": match["line"],
                                "content": match["content"],
                                "impact": "medium",
                                "dynamic_risk_reason": None
                            }
                            dependencies.append(dep)
                
                if self.cache:
                    self.cache.update_file_cache(file_path, dependencies)
            except:
                continue
        
        return dependencies
    
    def _find_matches(self, content: str, term: str) -> List[Dict]:
        """查找匹配"""
        matches = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if term.lower() in line.lower():
                matches.append({
                    "line": i,
                    "content": line.strip()[:100]
                })
        
        return matches
    
    def _apply_dynamic_risk(self) -> None:
        """应用动态风险评估"""
        impact_rules = self.config.get("impact_rules", {})
        
        for dep in self.results["dependencies"]:
            file_path = dep["file"].lower()
            
            # 静态风险评估
            for level, rule in impact_rules.items():
                keywords = rule.get("keywords", [])
                if any(kw in file_path for kw in keywords):
                    dep["impact"] = level
                    break
            
            # 动态风险评估
            dynamic_impact = self.dynamic_risk.evaluate_risk(dep)
            if dynamic_impact != dep["impact"]:
                dep["impact"] = dynamic_impact
                dep["dynamic_risk_reason"] = self.dynamic_risk.get_risk_reason(dep)
                self.results["dynamic_risks"].append(dep["file"])
    
    def generate_report(self, format: str = "markdown") -> str:
        """生成报告"""
        if format == "json":
            return json.dumps(self.results, indent=2, ensure_ascii=False)
        else:
            return self._generate_markdown()
    
    def _generate_markdown(self) -> str:
        """生成Markdown报告"""
        lines = [
            "# 蝴蝶效应扫描报告 v3.0",
            "",
            f"**目标**: {self.results['target']}",
            f"**扫描时间**: {self.results['scan_time']}",
            f"**扫描模式**: {self.results['performance'].get('scan_mode', 'full')}",
            ""
        ]
        
        # 性能统计
        perf = self.results["performance"]
        lines.extend([
            "## 性能统计",
            "",
            f"- 总文件: {perf['total_files']}",
            f"- 缓存文件: {perf['cached_files']}",
            f"- 实际扫描: {perf['scanned_files']}",
            f"- 扫描耗时: {perf['scan_duration_ms']}ms",
            ""
        ])
        
        # 动态风险统计
        if self.results["dynamic_risks"]:
            lines.extend([
                "## 动态风险评估",
                "",
                f"- 智能调整: {len(self.results['dynamic_risks'])}个文件",
                "- 基于历史失败数据调整风险等级",
                ""
            ])
        
        # 依赖统计
        deps = self.results["dependencies"]
        high = [d for d in deps if d["impact"] == "high"]
        medium = [d for d in deps if d["impact"] == "medium"]
        low = [d for d in deps if d["impact"] == "low"]
        
        lines.append(f"## 发现依赖 ({len(deps)}个)")
        lines.append("")
        
        if high:
            lines.append(f"### [HIGH] ({len(high)}个)")
            lines.append("| 文件 | 类型 | 引用 | 动态原因 |")
            lines.append("|------|------|------|----------|")
            for d in high:
                reason = d.get("dynamic_risk_reason") or "-"
                lines.append(f"| {d['file']} | {d['type']} | Line {d['line']} | {reason} |")
            lines.append("")
        
        if medium:
            lines.append(f"### [MEDIUM] ({len(medium)}个)")
            lines.append("| 文件 | 类型 | 引用 |")
            lines.append("|------|------|------|")
            for d in medium:
                lines.append(f"| {d['file']} | {d['type']} | Line {d['line']} |")
            lines.append("")
        
        if low:
            lines.append(f"### [LOW] ({len(low)}个)")
            lines.append("| 文件 | 类型 | 引用 |")
            lines.append("|------|------|------|")
            for d in low:
                lines.append(f"| {d['file']} | {d['type']} | Line {d['line']} |")
            lines.append("")
        
        lines.extend([
            "---",
            "*蝴蝶效应扫描器 v3.0 | 配置文件 + 历史数据库 + 动态风险评估*"
        ])
        
        return '\n'.join(lines)
    
    def save_report(self, output_path: str, format: str = "markdown") -> None:
        """保存报告"""
        report = self.generate_report(format)
        Path(output_path).write_text(report, encoding='utf-8')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="蝴蝶效应扫描器 v3.0")
    parser.add_argument("target", help="目标")
    parser.add_argument("--workspace", default=".", help="workspace路径")
    parser.add_argument("--terms", nargs="+", help="搜索词")
    parser.add_argument("--output", help="输出路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--incremental", action="store_true", help="增量扫描")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    
    args = parser.parse_args()
    
    search_terms = args.terms or [args.target]
    
    # 创建扫描器
    scanner = ButterflyScanner(args.workspace)
    
    # 如果指定--no-cache，临时禁用
    if args.no_cache:
        scanner.cache = None
    
    # 执行扫描
    results = scanner.scan(args.target, search_terms, incremental=args.incremental)
    
    # 保存报告
    ext = "json" if args.format == "json" else "md"
    output_path = args.output or f"butterfly_report_{args.target}.{ext}"
    scanner.save_report(output_path, args.format)
    
    # 输出摘要
    perf = results["performance"]
    print(f"[OK] v3.0扫描完成")
    print(f"  - 模式: {perf['scan_mode']}")
    print(f"  - 文件: {perf['total_files']}")
    print(f"  - 缓存: {perf['cached_files']}")
    print(f"  - 扫描: {perf['scanned_files']}")
    print(f"  - 耗时: {perf['scan_duration_ms']}ms")
    print(f"  - 动态风险调整: {len(results['dynamic_risks'])}个")
    print(f"  - 报告: {output_path}")


if __name__ == "__main__":
    main()