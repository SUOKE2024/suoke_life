#!/usr/bin/env python3
"""
索克生活无障碍服务 - UV 迁移验证脚本
验证 Python 3.13.3 和 UV 包管理器迁移是否完成
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

def check_python_version() -> Tuple[bool, str]:
    """检查 Python 版本"""
    version = sys.version_info
    if version.major == 3 and version.minor == 13 and version.micro >= 3:
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"❌ Python {version.major}.{version.minor}.{version.micro} (需要 3.13.3+)"

def check_uv_installation() -> Tuple[bool, str]:
    """检查 UV 工具安装"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"✅ UV {result.stdout.strip()}"
        else:
            return False, "❌ UV 未正确安装"
    except FileNotFoundError:
        return False, "❌ UV 未安装"

def check_pyproject_toml() -> Tuple[bool, str]:
    """检查 pyproject.toml 配置"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        return False, "❌ pyproject.toml 文件不存在"
    
    try:
        content = pyproject_path.read_text()
        if 'requires-python = ">=3.13.3"' in content:
            return True, "✅ pyproject.toml 配置正确 (Python 3.13.3+)"
        else:
            return False, "❌ pyproject.toml 中 Python 版本配置不正确"
    except Exception as e:
        return False, f"❌ 读取 pyproject.toml 失败: {e}"

def check_uv_lock() -> Tuple[bool, str]:
    """检查 uv.lock 文件"""
    uv_lock_path = Path("uv.lock")
    if uv_lock_path.exists():
        return True, "✅ uv.lock 文件存在"
    else:
        return False, "❌ uv.lock 文件不存在"

def check_project_structure() -> Tuple[bool, str]:
    """检查项目结构"""
    required_dirs = [
        "accessibility_service",
        "tests",
        "docs",
        "scripts",
        "deploy"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if not missing_dirs:
        return True, "✅ 项目结构完整"
    else:
        return False, f"❌ 缺少目录: {', '.join(missing_dirs)}"

def check_old_files() -> Tuple[bool, str]:
    """检查是否存在旧的配置文件"""
    old_files = [
        "requirements.txt",
        "setup.py",
        "setup.cfg",
        "Pipfile",
        "Pipfile.lock",
        "poetry.lock"
    ]
    
    found_old_files = []
    for file_name in old_files:
        if Path(file_name).exists():
            found_old_files.append(file_name)
    
    if not found_old_files:
        return True, "✅ 无旧配置文件"
    else:
        return False, f"⚠️ 发现旧配置文件: {', '.join(found_old_files)}"

def check_core_modules() -> Tuple[bool, str]:
    """检查核心模块是否存在"""
    core_modules = [
        "accessibility_service/__init__.py",
        "accessibility_service/core/service.py",
        "accessibility_service/models/accessibility.py",
        "accessibility_service/config/settings.py"
    ]
    
    missing_modules = []
    for module_path in core_modules:
        if not Path(module_path).exists():
            missing_modules.append(module_path)
    
    if not missing_modules:
        return True, "✅ 核心模块完整"
    else:
        return False, f"❌ 缺少核心模块: {', '.join(missing_modules)}"

def main():
    """主验证函数"""
    print("🔍 索克生活无障碍服务 - UV 迁移验证")
    print("=" * 50)
    
    checks = [
        ("Python 版本", check_python_version),
        ("UV 工具安装", check_uv_installation),
        ("pyproject.toml 配置", check_pyproject_toml),
        ("uv.lock 文件", check_uv_lock),
        ("项目结构", check_project_structure),
        ("旧文件清理", check_old_files),
        ("核心模块", check_core_modules),
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            results.append((check_name, passed, message))
            if not passed:
                all_passed = False
        except Exception as e:
            results.append((check_name, False, f"❌ 检查失败: {e}"))
            all_passed = False
    
    # 显示结果
    for check_name, passed, message in results:
        print(f"{check_name:20}: {message}")
    
    print("=" * 50)
    if all_passed:
        print("🎉 所有检查通过！UV 迁移已完成。")
        print("📋 项目状态:")
        print("   - ✅ Python 3.13.3 已配置")
        print("   - ✅ UV 包管理器已就绪")
        print("   - ✅ 现代化项目结构已建立")
        print("   - ✅ 遵循 Python 最佳实践")
        return 0
    else:
        print("⚠️ 部分检查未通过，请查看上述详情。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 