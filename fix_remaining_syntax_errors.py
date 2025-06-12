#!/usr/bin/env python3
"""
修复剩余Python语法错误的脚本
"""

import os
import re


def fix_remaining_syntax_errors(file_path):
    """修复单个文件的剩余语法错误"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # 修复各种运算符的空格问题
        content = re.sub(r" \*\* ", "**", content)
        content = re.sub(r" // ", "//", content)
        content = re.sub(r" /= ", "/=", content)
        content = re.sub(r" >= ", ">=", content)
        content = re.sub(r" <= ", "<=", content)
        content = re.sub(r"> = ", ">=", content)
        content = re.sub(r"< = ", "<=", content)
        content = re.sub(r"= = ", "==", content)
        content = re.sub(r"! = ", "!=", content)
        content = re.sub(r"\+== ", "+=", content)  # 修复 +== 错误

        # 修复除法赋值运算符
        content = re.sub(r"signal_power / = ", "signal_power /= ", content)
        content = re.sub(r"noise_power / = ", "noise_power /= ", content)

        # 修复幂运算符
        content = re.sub(r"\* \* ", "**", content)

        # 修复整除运算符
        content = re.sub(r"/ / ", "//", content)

        # 修复比较运算符
        content = re.sub(r"> = ", ">=", content)
        content = re.sub(r"< = ", "<=", content)

        # 修复特殊的语法错误
        content = re.sub(r">=== ", ">=", content)  # 修复三个等号的问题

        # 修复换行符问题 - 移除不必要的换行符转义
        content = re.sub(r"\\n\s*", "\n", content)

        # 只有内容发生变化时才写入文件
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"修复了文件: {file_path}")
            return True
        return False

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return False


def main():
    """主函数"""
    # 特定需要修复的文件
    problem_files = [
        "services/diagnostic-services/palpation-service/palpation_service/internal/enhanced_palpation_service.py",
        "services/diagnostic-services/five-diagnosis-orchestrator/five_diagnosis_orchestrator/utils/resource_manager.py",
        "services/utility-services/utility_services/integration_service/services/health_data_service.py",
    ]

    fixed_count = 0
    for file_path in problem_files:
        if os.path.exists(file_path):
            if fix_remaining_syntax_errors(file_path):
                fixed_count += 1
        else:
            print(f"文件不存在: {file_path}")

    print(f"修复了 {fixed_count} 个文件")


if __name__ == "__main__":
    main()
