#!/usr/bin/env python3
"""
备份文件恢复脚本
恢复 calculation-service 的所有备份文件
"""

import shutil
from pathlib import Path


def restore_backup_files():
    """恢复所有备份文件"""
    service_root = Path(__file__).parent
    backup_files = []

    # 查找所有备份文件
    for backup_file in service_root.rglob("*.backup"):
        original_file = backup_file.with_suffix("")
        backup_files.append((backup_file, original_file))

    print(f"发现 {len(backup_files)} 个备份文件")

    # 恢复备份文件
    restored_count = 0
    for backup_file, original_file in backup_files:
        try:
            # 确保目标目录存在
            original_file.parent.mkdir(parents=True, exist_ok=True)

            # 复制备份文件到原始位置
            shutil.copy2(backup_file, original_file)
            print(f"✅ 恢复: {original_file.relative_to(service_root)}")
            restored_count += 1

        except Exception as e:
            print(f"❌ 恢复失败 {original_file.relative_to(service_root)}: {e}")

    print(f"\n恢复完成: {restored_count}/{len(backup_files)} 个文件")
    return restored_count == len(backup_files)


if __name__ == "__main__":
    success = restore_backup_files()
    if success:
        print("🎉 所有备份文件恢复成功！")
    else:
        print("⚠️ 部分文件恢复失败，请检查错误信息")
