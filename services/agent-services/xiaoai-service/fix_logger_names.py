#!/usr/bin/env python3
"""

from loguru import logger
import os



批量修复 xiaoai-self.service 中的 self.logger 名称错误
将 _name__ 修复为 __name__
"""


def fix_logger_names(directory: str):
    pass
    """修复目录中所有 Python 文件的 self.logger 名称错误"""
    fixed_files = []
    error_files = []

    # 查找所有 Python 文件
    for root, dirs, files in os.walk(directory):
    pass
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.ruff_cache', '.mypy_cache']]
        :
        for file in files:
    pass
            if file.endswith('.py'):
    pass
                file_path = os.path.join(root, file)
                try:
    pass
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
    pass
                        content = f.read()

                    # 检查是否包含错误的 _name__
                    if '_name__' in content:
    pass
                        # 修复错误
                        new_content = content.replace('_name__', '__name__')

                        # 写回文件
                        with open(file_path, 'w', encoding='utf-8') as f:
    pass
                            f.write(new_content)

                        fixed_files.append(file_path)
                        print(f"✅ 修复: {file_path}")

                except Exception as e:
    pass
                    error_files.append((file_path, str(e)))
                    print(f"❌ 错误: {file_path} - {e}")

    return fixed_files, error_files

def main():
    pass
    """主函数"""
    print("开始修复 xiaoai-self.service 中的 self.logger 名称错误...")

    # 当前目录应该是 xiaoai-self.service 根目录
    xiaoai_dir = "./xiaoai"

    if not os.path.exists(xiaoai_dir):
    pass
        print(f"❌ 错误: 找不到 xiaoai 目录: {xiaoai_dir}")
        return

    fixed_files, error_files = fix_logger_names(xiaoai_dir)

    print(f"\n修复完成!")
    print(f"✅ 成功修复文件数: {len(fixed_files)}")
    print(f"❌ 错误文件数: {len(error_files)}")

    if error_files:
    pass
        print("\n错误文件列表:")
        for file_path, error in error_files:
    pass
            print(f"  - {file_path}: {error}")

if __name__ == "__main__":
    pass
    main()
