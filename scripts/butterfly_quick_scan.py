#!/usr/bin/env python3
"""
蝴蝶效应快速扫描器 v1.0 - 轻量级依赖检查（30秒完成）

用途：
  - 快速预判依赖风险（适合其他Agent）
  - 30秒内完成依赖检查
  - 分级评估（HIGH/MEDIUM/LOW）

使用方法：
  python butterfly_quick_scan.py <target> [--workspace <path>] [--output <format>]

参数：
  target: 要扫描的目标（文件名/模块名/配置名）
  --workspace: 工作目录（默认当前目录）
  --output: 输出格式（text/json，默认text）
  --limit: 最大结果数（默认50）

分级规则：
  HIGH: startup, health, cron, task, gateway, service, import
  MEDIUM: readme, guide, example, tutorial, config
  LOW: memory, history, archive, log
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import subprocess

# 分级关键词
HIGH_KEYWORDS = ["startup", "health", "cron", "task", "gateway", "service", "import", "require", "from", "load", "init"]
MEDIUM_KEYWORDS = ["readme", "guide", "example", "tutorial", "config", "setting", "option", "param"]
LOW_KEYWORDS = ["memory", "history", "archive", "log", "note", "temp", "cache"]

# 快速搜索的文件类型（核心类型）
QUICK_EXTENSIONS = ["py", "js", "ts", "ps1", "sh", "bat", "json", "yaml", "yml", "xml", "md"]

def generate_search_terms(target: str) -> List[str]:
    """生成搜索词变体"""
    terms = [
        target,                      # 直接名称
        f"/{target}",                # 路径形式
        target.replace("-", "_"),    # 下划线变体
        target.replace("_", "-"),    # 连字符变体
        target.replace(".", "/"),    # 点转路径
        f'"{target}"',               # 引号包裹
        f"'{target}'",               # 单引号包裹
    ]
    return terms

def quick_search(term: str, workspace: Path, limit: int = 50) -> List[Dict]:
    """快速搜索（使用grep或Python内置）"""
    results = []
    
    # 方法1: 尝试使用rg（ripgrep，更快）
    try:
        cmd = ["rg", "-l", "--max-count", str(limit), term, str(workspace)]
        output = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if output.returncode == 0:
            for line in output.stdout.strip().split("\n")[:limit]:
                if line and Path(line).exists():
                    results.append({"file": line, "term": term, "method": "rg"})
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # 方法2: 如果rg失败，使用grep
    if not results:
        try:
            cmd = ["grep", "-r", "-l", "--exclude-dir=.git", term, str(workspace)]
            output = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if output.returncode == 0:
                for line in output.stdout.strip().split("\n")[:limit]:
                    if line and Path(line).exists():
                        results.append({"file": line, "term": term, "method": "grep"})
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    # 方法3: 如果grep失败，使用Python内置搜索
    if not results:
        results = python_search(term, workspace, limit)
    
    return results

def python_search(term: str, workspace: Path, limit: int = 50) -> List[Dict]:
    """Python内置搜索（最慢但可靠）"""
    results = []
    
    for ext in QUICK_EXTENSIONS:
        for file_path in workspace.rglob(f"*.{ext}"):
            # 排除目录
            if any(skip in str(file_path) for skip in [".git", ".bak", "node_modules", "__pycache__", "dist", "build"]):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if term in content:
                        # 找到匹配行
                        for i, line in enumerate(content.split("\n"), 1):
                            if term in line:
                                results.append({
                                    "file": str(file_path),
                                    "line": i,
                                    "content": line.strip()[:100],
                                    "term": term,
                                    "method": "python"
                                })
                                if len(results) >= limit:
                                    return results
            except Exception:
                continue
    
    return results

def classify_impact(result: Dict) -> str:
    """分级评估"""
    content = result.get("content", "").lower()
    file_path = result.get("file", "").lower()
    
    # 检查HIGH关键词
    for kw in HIGH_KEYWORDS:
        if kw in content or kw in file_path:
            return "HIGH"
    
    # 检查MEDIUM关键词
    for kw in MEDIUM_KEYWORDS:
        if kw in content or kw in file_path:
            return "MEDIUM"
    
    # 默认LOW
    return "LOW"

def quick_butterfly_check(target: str, workspace: Path, limit: int = 50) -> Dict:
    """30秒内完成的依赖检查"""
    start_time = datetime.now()
    
    # 生成搜索词
    terms = generate_search_terms(target)
    
    # 快速搜索
    all_results = []
    for term in terms:
        results = quick_search(term, workspace, limit)
        all_results.extend(results)
    
    # 去重
    unique_results = []
    seen_files = set()
    for result in all_results:
        file_key = result.get("file", "")
        if file_key not in seen_files:
            seen_files.add(file_key)
            unique_results.append(result)
    
    # 分级
    classified = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for result in unique_results[:limit]:
        impact = classify_impact(result)
        classified[impact].append(result)
    
    # 计算耗时
    elapsed = (datetime.now() - start_time).total_seconds()
    
    return {
        "target": target,
        "workspace": str(workspace),
        "scan_time": datetime.now().isoformat(),
        "elapsed_seconds": round(elapsed, 2),
        "total_found": len(unique_results),
        "classified": classified,
        "high_count": len(classified["HIGH"]),
        "medium_count": len(classified["MEDIUM"]),
        "low_count": len(classified["LOW"]),
        "method": "quick_scan"
    }

def format_text_output(data: Dict) -> str:
    """格式化文本输出"""
    lines = []
    lines.append(f"# 🦋 Butterfly Quick Scan Report")
    lines.append(f"")
    lines.append(f"**Target**: {data['target']}")
    lines.append(f"**Workspace**: {data['workspace']}")
    lines.append(f"**Scan Time**: {data['scan_time']}")
    lines.append(f"**Elapsed**: {data['elapsed_seconds']}s")
    lines.append(f"**Total Found**: {data['total_found']}")
    lines.append(f"")
    
    # HIGH
    if data["high_count"] > 0:
        lines.append(f"## 🔴 [HIGH] High Impact ({data['high_count']})")
        for result in data["classified"]["HIGH"]:
            lines.append(f"- `{Path(result['file']).name}` - Line {result.get('line', '?')}: {result.get('content', '')[:50]}")
        lines.append(f"")
    
    # MEDIUM
    if data["medium_count"] > 0:
        lines.append(f"## 🟡 [MEDIUM] Medium Impact ({data['medium_count']})")
        for result in data["classified"]["MEDIUM"]:
            lines.append(f"- `{Path(result['file']).name}` - Line {result.get('line', '?')}: {result.get('content', '')[:50]}")
        lines.append(f"")
    
    # LOW
    if data["low_count"] > 0:
        lines.append(f"## 🟢 [LOW] Low Impact ({data['low_count']})")
        for result in data["classified"]["LOW"]:
            lines.append(f"- `{Path(result['file']).name}` - Line {result.get('line', '?')}: {result.get('content', '')[:50]}")
        lines.append(f"")
    
    # 建议
    lines.append(f"## Recommended Actions")
    if data["high_count"] > 0:
        lines.append(f"- 🔴 Must handle HIGH dependencies first ({data['high_count']} items)")
    if data["medium_count"] > 0:
        lines.append(f"- 🟡 Recommended to check MEDIUM dependencies ({data['medium_count']} items)")
    if data["low_count"] > 0:
        lines.append(f"- 🟢 LOW dependencies can be kept ({data['low_count']} items)")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"**Quick Scan v1.0 | 30s elapsed: {data['elapsed_seconds']}s**")
    
    return "\n".join(lines)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="蝴蝶效应快速扫描器（30秒完成）")
    parser.add_argument("target", help="要扫描的目标（文件名/模块名/配置名）")
    parser.add_argument("--workspace", default=".", help="工作目录（默认当前目录）")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="输出格式")
    parser.add_argument("--limit", type=int, default=50, help="最大结果数")
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        print(f"[ERROR] Workspace not found: {workspace}")
        sys.exit(1)
    
    print(f"[INFO] Starting quick scan for: {args.target}")
    print(f"[INFO] Workspace: {workspace}")
    print(f"[INFO] Max results: {args.limit}")
    
    # 执行快速扫描
    data = quick_butterfly_check(args.target, workspace, args.limit)
    
    # 输出
    if args.output == "json":
        print(json.dumps(data, indent=2))
    else:
        print(format_text_output(data))
    
    # 如果HIGH风险超过5个，建议跑完整扫描
    if data["high_count"] > 5:
        print(f"\n[WARN] HIGH dependencies > 5, recommend full scan:")
        print(f"       python butterfly_scan.py {args.target}")

if __name__ == "__main__":
    main()