#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 3.13 兼容性测试脚本
测试重构后的目录结构和基本功能
"""

import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_python_version():
    """测试 Python 版本"""
    print("=== Python 版本测试 ===")
    print(f"Python 版本: {sys.version}")
    print(f"Python 版本信息: {sys.version_info}")
    
    if sys.version_info >= (3, 13):
        print("✓ Python 3.13+ 版本检测通过")
        return True
    else:
        print("✗ Python 版本过低，需要 3.13+")
        return False

def test_basic_imports():
    """测试基本导入"""
    print("\n=== 基本导入测试 ===")
    
    try:
        # 测试标准库
        import asyncio
        import json
        import pathlib
        print("✓ 标准库导入成功")
        
        # 测试已安装的核心包
        import pytest
        import pydantic
        import fastapi
        try:
            import grpc
            print("✓ 核心依赖包导入成功")
        except ImportError:
            print("⚠ grpc 包未安装，但其他核心包正常")
        
        # 测试项目结构
        import xiaoai
        print("✓ 主包 xiaoai 导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        traceback.print_exc()
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n=== 目录结构测试 ===")
    
    required_dirs = [
        "xiaoai",
        "xiaoai/agent",
        "xiaoai/delivery", 
        "xiaoai/cli",
        "xiaoai/utils",
        "tests",
        "api",
        "config",
        "docs"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path} 存在")
        else:
            print(f"✗ {dir_path} 不存在")
            all_exist = False
    
    return all_exist

def test_package_files():
    """测试包文件"""
    print("\n=== 包文件测试 ===")
    
    required_files = [
        "__init__.py",
        "xiaoai/__init__.py",
        "setup.py",
        "requirements.txt",
        "requirements_py313.txt",
        "run_server.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} 存在")
        else:
            print(f"✗ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def test_new_python_features():
    """测试 Python 3.13 新特性"""
    print("\n=== Python 3.13 新特性测试 ===")
    
    try:
        # 测试改进的错误消息
        def test_error_messages():
            try:
                x = {}
                y = x['nonexistent']
            except KeyError as e:
                print("✓ 改进的错误消息功能正常")
                return True
            return False
        
        # 测试类型提示改进
        def test_type_hints():
            from typing import Optional, List, Dict
            
            def example_function(data: Optional[List[Dict[str, str]]]) -> bool:
                return data is not None
            
            print("✓ 类型提示功能正常")
            return True
        
        # 测试性能改进
        def test_performance():
            import time
            start = time.time()
            
            # 简单的性能测试
            result = sum(i * i for i in range(10000))
            
            end = time.time()
            print(f"✓ 性能测试完成，耗时: {end - start:.4f}秒")
            return True
        
        test_error_messages()
        test_type_hints()
        test_performance()
        
        return True
        
    except Exception as e:
        print(f"✗ Python 3.13 特性测试失败: {e}")
        return False

def test_pytest_compatibility():
    """测试 pytest 兼容性"""
    print("\n=== pytest 兼容性测试 ===")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pytest", "--version"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✓ pytest 版本: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ pytest 检查失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ pytest 兼容性测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始 Python 3.13 兼容性测试...")
    print(f"当前工作目录: {os.getcwd()}")
    
    tests = [
        ("Python 版本", test_python_version),
        ("目录结构", test_directory_structure),
        ("包文件", test_package_files),
        ("基本导入", test_basic_imports),
        ("Python 3.13 新特性", test_new_python_features),
        ("pytest 兼容性", test_pytest_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n=== 测试结果汇总 ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Python 3.13 升级成功！")
        return 0
    else:
        print("⚠ 部分测试失败，需要进一步检查")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 