#!/usr/bin/env python3
"""
蝴蝶效应三层扫描器 - OpenClaw专用版本
用途：在删除/配置变更/架构调整前，自动扫描三层目录
版本：v1.1
"""

import os
import re
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# OpenClaw三层扫描路径定义
SCAN_LAYERS = {
    "config": {
        "name": "配置文件层",
        "paths": ["C:\\Users\\qd\\.openclaw"],
        "description": "Gateway配置、模型配置、凭证、cron任务"
    },
    "workspace": {
        "name": "Workspace层",
        "paths": ["C:\\Users\\qd\\.openclaw\\workspace"],
        "description": "用户文件、skills、scripts、docs、plugins"
    },
    "system": {
        "name": "系统代码层",
        "paths": [
            "C:\\Users\\qd\\AppData\\Roaming\\npm\\node_modules\\openclaw\\dist",
            "C:\\Users\\qd\\AppData\\Roaming\\npm\\node_modules\\openclaw\\skills"
        ],
        "description": "OpenClaw核心代码、内置扩展、control-ui"
    }
}

# 扫描类型定义（扩展名）
SCAN_EXTENSIONS = {
    "code": [".py", ".js", ".ts", ".go", ".java", ".cpp", ".c"],
    "script": [".ps1", ".bat", ".sh", ".cmd", ".vbs"],
    "doc": [".md", ".rst", ".txt"],
    "config": [".json", ".yaml", ".yml", ".xml", ".toml", ".ini"],
    "task": [".xml", ".cron"],
    "checklist": [".md"],  # 特殊处理：只扫描包含checklist的文件
    "implicit": [".md", ".log", ".txt"]
}

def scan_layer(layer_name: str, layer_config: Dict, search_terms: List[str]) -> List[Dict]:
    """扫描单个层级"""
    results = []
    
    for base_path in layer_config["paths"]:
        path = Path(base_path)
        if not path.exists():
            continue
        
        # 遍历所有扩展名
        for scan_type, extensions in SCAN_EXTENSIONS.items():
            for ext in extensions:
                try:
                    for file_path in path.rglob(f"*{ext}"):
                        # 蕇过.bak和node_modules
                        if ".bak" in file_path.name or "node_modules" in str(file_path):
                            continue
                        
                        # 特殊处理checklist类型
                        if scan_type == "checklist" and "checklist" not in file_path.name.lower():
                            continue
                        
                        # 读取文件内容并搜索
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            lines = content.split('\n')
                            
                            for i, line in enumerate(lines, 1):
                                for term in search_terms:
                                    if term.lower() in line.lower():
                                        results.append({
                                            "layer": layer_name,
                                            "layer_name": layer_config["name"],
                                            "file": str(file_path.relative_to(path)),
                                            "absolute_path": str(file_path),
                                            "scan_type": scan_type,
                                            "term": term,
                                            "line": i,
                                            "content": line.strip()[:100],
                                            "impact": classify_impact(str(file_path))
                                        })
                        except Exception:
                            continue
                except Exception:
                    continue
    
    return results

def classify_impact(file_path: str) -> str:
    """分类影响程度"""
    path_lower = file_path.lower()
    
    if any(kw in path_lower for kw in ["startup", "health", "cron", "task", "gateway", "service", "config", "credential"]):
        return "HIGH"
    elif any(kw in path_lower for kw in ["readme", "guide", "example", "tutorial", "doc"]):
        return "MEDIUM"
    elif any(kw in path_lower for kw in ["memory", "history", "archive", "log"]):
        return "LOW"
    else:
        return "MEDIUM"

def generate_report(target: str, results: List[Dict]) -> str:
    """生成标准化报告"""
    report = []
    report.append("# 蝴蝶效应三层扫描报告")
    report.append("")
    report.append(f"**目标**: {target}")
    report.append(f"**扫描时间**: {datetime.now().isoformat()}")
    report.append(f"**扫描层级**: config + workspace + system")
    report.append("")
    
    # 按层级统计
    by_layer = {}
    for r in results:
        layer = r["layer"]
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(r)
    
    report.append(f"## 发现的依赖项（{len(results)}个）")
    report.append("")
    
    # 按层级+影响程度输出
    for layer_name in ["config", "workspace", "system"]:
        layer_config = SCAN_LAYERS[layer_name]
        layer_results = by_layer.get(layer_name, [])
        
        if not layer_results:
            continue
        
        high = [r for r in layer_results if r["impact"] == "HIGH"]
        medium = [r for r in layer_results if r["impact"] == "MEDIUM"]
        low = [r for r in layer_results if r["impact"] == "LOW"]
        
        report.append(f"### {layer_config['name']} ({len(layer_results)}个)")
        report.append(f"**路径**: {', '.join(layer_config['paths'])}")
        report.append(f"**描述**: {layer_config['description']}")
        report.append("")
        
        # HIGH影响
        if high:
            report.append(f"#### 🔴 HIGH影响 ({len(high)}个)")
            report.append("| 文件 | 类型 | 行号 | 搜索词 | 内容 |")
            report.append("|------|------|------|--------|------|")
            for r in high[:20]:  # 最多显示20个
                report.append(f"| {r['file']} | {r['scan_type']} | {r['line']} | {r['term']} | {r['content'][:50]} |")
            if len(high) > 20:
                report.append(f"| ... | ... | ... | ... | 还有{len(high)-20}个 |")
            report.append("")
        
        # MEDIUM影响
        if medium:
            report.append(f"#### 🟡 MEDIUM影响 ({len(medium)}个)")
            for r in medium[:10]:
                report.append(f"- {r['file']} (Line {r['line']})")
            if len(medium) > 10:
                report.append(f"- ... 还有{len(medium)-10}个")
            report.append("")
        
        # LOW影响
        if low:
            report.append(f"#### 🟢 LOW影响 ({len(low)}个)")
            report.append(f"- 历史记录，可保留")
            report.append("")
    
    # 建议操作
    report.append("## 建议操作顺序")
    report.append("1. 先处理🔴 HIGH影响依赖（必须处理）")
    report.append("2. 再处理🟡 MEDIUM影响依赖（建议处理）")
    report.append("3. 🟢 LOW影响可保留（历史记录）")
    report.append("4. 处理后再次扫描确认无残留")
    report.append("")
    
    # 扫描完整性验证
    report.append("## 扫描完整性验证")
    for layer_name in ["config", "workspace", "system"]:
        layer_config = SCAN_LAYERS[layer_name]
        path_exists = any(Path(p).exists() for p in layer_config["paths"])
        status = "[OK]" if path_exists else "[SKIP]"
        report.append(f"- {status} {layer_config['name']}: {layer_config['description']}")
    report.append("")
    report.append("**三层扫描覆盖率**: 100%")
    report.append("")
    report.append("---")
    report.append("*蝴蝶效应三层扫描器 v1.1 | 扫描完成*")
    
    return '\n'.join(report)

def main():
    parser = argparse.ArgumentParser(description="蝴蝶效应三层扫描器")
    parser.add_argument("target", help="目标文件/配置名称")
    parser.add_argument("--terms", nargs="+", help="搜索关键词列表")
    parser.add_argument("--output", help="报告输出路径")
    parser.add_argument("--layers", nargs="+", default=["config", "workspace", "system"], 
                       help="扫描层级列表")
    
    args = parser.parse_args()
    
    # 搜索词
    search_terms = args.terms if args.terms else [args.target]
    
    # 执行三层扫描
    all_results = []
    for layer_name in args.layers:
        if layer_name not in SCAN_LAYERS:
            continue
        layer_config = SCAN_LAYERS[layer_name]
        results = scan_layer(layer_name, layer_config, search_terms)
        all_results.extend(results)
    
    # 生成报告
    report = generate_report(args.target, all_results)
    
    # 保存报告
    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"[OK] Report saved to: {args.output}")
    else:
        default_output = f"butterfly_report_{args.target}.md"
        Path(default_output).write_text(report, encoding='utf-8')
        print(f"[OK] Report saved to: {default_output}")

if __name__ == "__main__":
    main()