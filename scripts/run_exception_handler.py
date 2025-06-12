#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# 添加脚本目录到路径
sys.path.append(os.path.dirname(__file__))

from create_unified_exception_handler import UnifiedExceptionHandler


def main():
    project_root = os.getcwd()
    print("🔧 索克生活项目 - 统一异常处理机制创建工具")
    print("=" * 60)

    handler = UnifiedExceptionHandler(project_root)

    # 1. 创建异常处理框架
    print("📦 创建统一异常处理框架...")
    exceptions_file, config_file = handler.create_exception_framework()

    # 2. 扫描现有异常处理模式
    print("🔍 扫描现有异常处理模式...")
    patterns = handler.scan_exception_patterns()

    # 3. 创建迁移脚本
    if patterns:
        print("📝 创建异常处理迁移脚本...")
        migration_script = handler.create_migration_script(patterns)

    # 4. 生成报告
    report = handler.generate_report(patterns)

    # 保存报告
    report_file = Path(project_root) / "exception_handling_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print()
    print("=" * 60)
    print("📄 异常处理框架创建完成！")
    print(f"📊 发现 {len(patterns)} 个需要改进的异常处理模式")
    print(f"📋 详细报告已保存到 exception_handling_report.md")
    print()
    print("🚀 下一步:")
    print("1. 查看报告了解具体问题")
    print("2. 运行迁移脚本修复问题")
    print("3. 在新代码中使用统一异常处理框架")


if __name__ == "__main__":
    main()
