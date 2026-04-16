#!/usr/bin/env python3
"""
蝴蝶效应可视化脚本
生成依赖关系图（HTML格式）
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

class ButterflyVisualizer:
    """依赖关系可视化"""
    
    def __init__(self, report_path: str):
        self.report_path = Path(report_path)
        self.report = self._load_report()
    
    def _load_report(self) -> dict:
        """加载JSON报告"""
        if self.report_path.exists():
            try:
                return json.loads(self.report_path.read_text(encoding='utf-8'))
            except:
                return {}
        return {}
    
    def generate_html(self) -> str:
        """生成HTML可视化报告"""
        deps = self.report.get("dependencies", [])
        target = self.report.get("target", "unknown")
        
        # 分组依赖
        high_deps = [d for d in deps if d.get("impact") == "high"]
        medium_deps = [d for d in deps if d.get("impact") == "medium"]
        low_deps = [d for d in deps if d.get("impact") == "low"]
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>蝴蝶效应可视化 - {target}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-box {{ background: white; padding: 15px; border-radius: 8px; flex: 1; text-align: center; }}
        .stat-high {{ border: 3px solid #e74c3c; }}
        .stat-medium {{ border: 3px solid #f39c12; }}
        .stat-low {{ border: 3px solid #27ae60; }}
        .stat-number {{ font-size: 24px; font-weight: bold; }}
        .section {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .dep-table {{ width: 100%; border-collapse: collapse; }}
        .dep-table th {{ background: #34495e; color: white; padding: 10px; }}
        .dep-table td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        .dep-table tr:hover {{ background: #f9f9f9; }}
        .tag-high {{ background: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; }}
        .tag-medium {{ background: #f39c12; color: white; padding: 3px 8px; border-radius: 3px; }}
        .tag-low {{ background: #27ae60; color: white; padding: 3px 8px; border-radius: 3px; }}
        .graph {{ margin: 20px 0; }}
        .node {{ display: inline-block; margin: 10px; padding: 10px; border-radius: 5px; }}
        .node-target {{ background: #667eea; color: white; }}
        .node-high {{ background: #e74c3c; color: white; }}
        .node-medium {{ background: #f39c12; color: white; }}
        .node-low {{ background: #27ae60; color: white; }}
        .arrow {{ color: #666; font-size: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦋 蝴蝶效应可视化报告</h1>
        <p>目标: {target} | 扫描时间: {self.report.get('scan_time', 'N/A')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-box stat-high">
            <div class="stat-number">{len(high_deps)}</div>
            <div>🔴 高影响</div>
        </div>
        <div class="stat-box stat-medium">
            <div class="stat-number">{len(medium_deps)}</div>
            <div>🟡 中影响</div>
        </div>
        <div class="stat-box stat-low">
            <div class="stat-number">{len(low_deps)}</div>
            <div>🟢 低影响</div>
        </div>
    </div>
    
    <div class="section">
        <h2>依赖关系图</h2>
        <div class="graph">
            <div class="node node-target">{target}</div>
            <span class="arrow">→</span>
"""
        
        # 添加节点
        for d in high_deps[:5]:
            html += f'<div class="node node-high">{Path(d["file"]).name}</div>\n'
        
        for d in medium_deps[:3]:
            html += f'<div class="node node-medium">{Path(d["file"]).name}</div>\n'
        
        for d in low_deps[:2]:
            html += f'<div class="node node-low">{Path(d["file"]).name}</div>\n'
        
        html += """
        </div>
    </div>
"""
        
        # 高影响表格
        if high_deps:
            html += """
    <div class="section">
        <h2>🔴 高影响依赖</h2>
        <table class="dep-table">
            <tr><th>文件</th><th>类型</th><th>引用位置</th><th>关键词</th></tr>
"""
            for d in high_deps:
                html += f'<tr><td>{d["file"]}</td><td>{d["type"]}</td><td>Line {d["line"]}</td><td>{d["term"]}</td></tr>\n'
            html += "</table></div>\n"
        
        # 中影响表格
        if medium_deps:
            html += """
    <div class="section">
        <h2>🟡 中影响依赖</h2>
        <table class="dep-table">
            <tr><th>文件</th><th>类型</th><th>引用位置</th><th>关键词</th></tr>
"""
            for d in medium_deps:
                html += f'<tr><td>{d["file"]}</td><td>{d["type"]}</td><td>Line {d["line"]}</td><td>{d["term"]}</td></tr>\n'
            html += "</table></div>\n"
        
        html += """
    <div class="section">
        <h2>建议操作</h2>
        <ol>
            <li>优先处理🔴高影响依赖</li>
            <li>再处理🟡中影响依赖</li>
            <li>🟢低影响可保留（历史记录）</li>
            <li>处理后再次扫描确认无残留</li>
        </ol>
    </div>
    
    <footer style="text-align: center; color: #666; margin: 40px 0;">
        蝴蝶效应扫描器 v3.0 | 可视化报告
    </footer>
</body>
</html>"""
        
        return html
    
    def save_html(self, output_path: str) -> None:
        """保存HTML报告"""
        html = self.generate_html()
        Path(output_path).write_text(html, encoding='utf-8')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="蝴蝶效应可视化")
    parser.add_argument("report", help="JSON报告路径")
    parser.add_argument("--output", default="butterfly_visual.html", help="输出路径")
    
    args = parser.parse_args()
    
    visualizer = ButterflyVisualizer(args.report)
    visualizer.save_html(args.output)
    
    print(f"[OK] 可视化报告生成: {args.output}")


if __name__ == "__main__":
    main()