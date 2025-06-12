#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.append(str(Path(__file__).parent / "scripts"))

try:
    from optimize_imports import ImportOptimizer

    def main():
        project_root = os.getcwd()
        print("📦 索克生活项目 - 导入语句优化工具")
        print("=" * 60)

        optimizer = ImportOptimizer(project_root)

        # 1. 扫描导入问题
        print("🔍 扫描导入问题...")
        issues = optimizer.scan_import_issues()

        # 2. 创建导入规范指南
        print("📝 创建导入规范指南...")
        guidelines_file = optimizer.create_import_guidelines()
        print(f"✅ 已创建导入规范指南: {guidelines_file}")

        # 3. 生成报告
        print("📊 生成报告...")
        report = optimizer.generate_report()

        # 保存报告
        report_file = Path(project_root) / "import_optimization_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📊 优化报告已保存到: {report_file}")

        if issues:
            print(f"\n⚠️  发现 {len(issues)} 个导入问题，请查看报告详情")
        else:
            print("\n✅ 未发现导入问题")

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保scripts/optimize_imports.py文件存在")
