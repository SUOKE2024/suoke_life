#!/usr/bin/env python3
"""
小艾智能体服务语法错误检查器
"""

import ast
import os
import json
from pathlib import Path
from typing import List, Dict, Any

def check_syntax_errors(directory: str) -> List[Dict[str, Any]]:
    """检查目录中所有Python文件的语法错误"""
    errors = []

    for root, dirs, files in os.walk(directory):
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', '.venv']]

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append({
                        'file': filepath,
                        'line': e.lineno,
                        'column': e.offset,
                        'message': e.msg,
                        'text': e.text.strip() if e.text else ''
                    })
                except UnicodeDecodeError as e:
                    errors.append({
                        'file': filepath,
                        'line': 0,
                        'column': 0,
                        'message': f'Unicode decode error: {e}',
                        'text': ''
                    })
                except Exception as e:
                    errors.append({
                        'file': filepath,
                        'line': 0,
                        'column': 0,
                        'message': f'Unexpected error: {e}',
                        'text': ''
                    })

    return errors

def main():
    """主函数"""
    xiaoai_service_dir = "services/agent-services/xiaoai-service"

    if not os.path.exists(xiaoai_service_dir):
        print(f"目录不存在: {xiaoai_service_dir}")
        return

    print("🔍 检查小艾智能体服务语法错误...")
    errors = check_syntax_errors(xiaoai_service_dir)

    print(f"\n📊 检查结果:")
    print(f"总语法错误数: {len(errors)}")

    if errors:
        print(f"\n🚨 前10个语法错误:")
        for i, error in enumerate(errors[:10], 1):
            print(f"{i}. {error['file']}:{error['line']} - {error['message']}")
            if error['text']:
                print(f"   代码: {error['text']}")

        # 保存详细错误报告
        with open('xiaoai_syntax_errors.json', 'w', encoding='utf-8') as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
        print(f"\n💾 详细错误报告已保存到: xiaoai_syntax_errors.json")

        # 统计错误类型
        error_types = {}
        for error in errors:
            msg = error['message']
            error_types[msg] = error_types.get(msg, 0) + 1

        print(f"\n📈 错误类型统计:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {error_type}: {count}次")
    else:
        print("✅ 没有发现语法错误!")

if __name__ == "__main__":
    main() 