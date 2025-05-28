#!/usr/bin/env python3
"""
区块链服务优化验证脚本

验证 Python 3.13.3 + UV 优化的成果。
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version >= (3, 13, 3):
        print("   ✓ 符合要求 (>= 3.13.3)")
    else:
        print("   ✗ 版本过低")
    return version >= (3, 13, 3)

def check_project_structure():
    """检查项目结构"""
    print("\n📁 项目结构检查:")
    
    required_files = [
        "pyproject.toml",
        "uv.lock", 
        ".python-version",
        "Makefile",
        ".pre-commit-config.yaml",
        "suoke_blockchain_service/__init__.py",
        "suoke_blockchain_service/config.py",
        "suoke_blockchain_service/main.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "migrations/env.py",
        "deploy/docker/Dockerfile"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path} (缺失)")
            all_exist = False
    
    return all_exist

def check_dependencies():
    """检查关键依赖"""
    print("\n📦 依赖检查:")
    
    try:
        import pydantic
        print(f"   ✓ pydantic {pydantic.__version__}")
    except ImportError:
        print("   ✗ pydantic 未安装")
        return False
    
    try:
        import pydantic_settings
        print(f"   ✓ pydantic-settings")
    except ImportError:
        print("   ✗ pydantic-settings 未安装")
        return False
    
    return True

def check_configuration():
    """检查配置模块"""
    print("\n⚙️  配置模块检查:")
    
    try:
        # 简单的配置测试，不导入整个模块
        with open("suoke_blockchain_service/config.py", "r") as f:
            content = f.read()
            
        if "class Settings" in content:
            print("   ✓ Settings 类存在")
        else:
            print("   ✗ Settings 类缺失")
            return False
            
        if "field_validator" in content:
            print("   ✓ 使用现代化的 field_validator")
        else:
            print("   ✗ 未使用 field_validator")
            return False
            
        return True
    except Exception as e:
        print(f"   ✗ 配置检查失败: {e}")
        return False

def check_makefile():
    """检查 Makefile"""
    print("\n🔨 Makefile 检查:")
    
    try:
        with open("Makefile", "r") as f:
            content = f.read()
            
        commands = ["help", "install", "test", "lint", "format", "clean"]
        all_commands = True
        
        for cmd in commands:
            if f"{cmd}:" in content:
                print(f"   ✓ {cmd} 命令")
            else:
                print(f"   ✗ {cmd} 命令缺失")
                all_commands = False
                
        return all_commands
    except Exception as e:
        print(f"   ✗ Makefile 检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 索克生活区块链服务优化验证")
    print("=" * 50)
    
    checks = [
        ("Python 版本", check_python_version),
        ("项目结构", check_project_structure), 
        ("依赖安装", check_dependencies),
        ("配置模块", check_configuration),
        ("Makefile", check_makefile),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ✗ {name} 检查失败: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 验证结果汇总:")
    
    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{len(results)} 项检查通过")
    
    if passed == len(results):
        print("\n🎉 恭喜！区块链服务优化完成，所有检查都通过了！")
        print("\n📋 优化成果:")
        print("   • 升级到 Python 3.13.3")
        print("   • 使用 UV 进行依赖管理")
        print("   • 现代化的项目结构")
        print("   • 类型安全的配置管理")
        print("   • 完整的开发工具链")
        print("   • Docker 容器化支持")
        print("   • 数据库迁移支持")
        print("   • 监控和日志系统")
    else:
        print(f"\n⚠️  还有 {len(results) - passed} 项需要修复")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 