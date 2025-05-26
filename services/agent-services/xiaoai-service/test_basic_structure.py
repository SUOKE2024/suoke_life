#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本结构测试脚本
验证重构后的目录结构和导入是否正常
"""

import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """测试基本导入"""
    print("=== 测试基本导入 ===")
    
    try:
        # 测试主包导入
        import xiaoai
        print("✓ 主包 xiaoai 导入成功")
        
        # 测试核心模块导入
        from xiaoai.agent import agent_manager
        print("✓ agent_manager 导入成功")
        
        from xiaoai.delivery import xiaoai_service_impl
        print("✓ xiaoai_service_impl 导入成功")
        
        # 测试配置模块
        try:
            from xiaoai.config import config_manager
            print("✓ config_manager 导入成功")
        except ImportError:
            print("⚠ config_manager 导入失败（可能不存在）")
        
        # 测试工具模块
        try:
            from xiaoai.utils import config_loader
            print("✓ config_loader 导入成功")
        except ImportError:
            print("⚠ config_loader 导入失败（可能不存在）")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        traceback.print_exc()
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n=== 测试目录结构 ===")
    
    expected_dirs = [
        "xiaoai",
        "xiaoai/agent",
        "xiaoai/delivery", 
        "xiaoai/cli",
        "xiaoai/four_diagnosis",
        "xiaoai/orchestrator",
        "xiaoai/repository",
        "xiaoai/service",
        "xiaoai/utils",
        "api",
        "tests",
        "config",
        "docs"
    ]
    
    missing_dirs = []
    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path} 存在")
        else:
            print(f"✗ {dir_path} 不存在")
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0

def test_package_files():
    """测试包文件"""
    print("\n=== 测试包文件 ===")
    
    expected_files = [
        "__init__.py",
        "xiaoai/__init__.py",
        "setup.py",
        "requirements.txt",
        "run_server.py",
        "PROJECT_STRUCTURE.md"
    ]
    
    missing_files = []
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} 存在")
        else:
            print(f"✗ {file_path} 不存在")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_cli_script():
    """测试CLI脚本"""
    print("\n=== 测试CLI脚本 ===")
    
    try:
        # 测试启动脚本是否可执行
        if os.path.exists("run_server.py"):
            print("✓ run_server.py 存在")
            
            # 检查是否可执行
            if os.access("run_server.py", os.X_OK):
                print("✓ run_server.py 可执行")
            else:
                print("⚠ run_server.py 不可执行")
        
        # 测试CLI模块导入
        try:
            from xiaoai.cli import main
            print("✓ CLI main 模块导入成功")
        except ImportError as e:
            print(f"⚠ CLI main 模块导入失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ CLI测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试 xiaoai-service 重构后的结构...")
    print(f"当前工作目录: {os.getcwd()}")
    
    tests = [
        ("目录结构", test_directory_structure),
        ("包文件", test_package_files),
        ("基本导入", test_basic_imports),
        ("CLI脚本", test_cli_script),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n=== 测试结果汇总 ===")
    passed = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！xiaoai-service 结构重构成功！")
        return 0
    else:
        print("⚠ 部分测试失败，需要进一步检查")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 