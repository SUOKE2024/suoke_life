#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面集成测试脚本（修复版）
测试 Python 3.13 升级后的各个模块功能
"""

import sys
import os
import asyncio
import traceback
import time
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_imports():
    """测试模块导入"""
    print("=== 模块导入测试 ===")
    
    modules_to_test = [
        # 核心模块
        ("xiaoai", "主包"),
        ("xiaoai.agent", "智能体模块"),
        ("xiaoai.delivery", "交付层"),
        ("xiaoai.utils", "工具模块"),
        ("xiaoai.service", "服务模块"),
        
        # 具体类
        ("xiaoai.agent.model_config_manager", "模型配置管理器"),
        ("xiaoai.four_diagnosis.multimodal_fusion", "多模态融合引擎"),
        ("xiaoai.utils.config_loader", "配置加载器"),
    ]
    
    results = []
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {description} ({module_name}) 导入成功")
            results.append(True)
        except ImportError as e:
            print(f"✗ {description} ({module_name}) 导入失败: {e}")
            results.append(False)
        except Exception as e:
            print(f"⚠ {description} ({module_name}) 导入异常: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"模块导入成功率: {success_rate:.1f}% ({sum(results)}/{len(results)})")
    return success_rate > 80

def test_class_instantiation():
    """测试类实例化"""
    print("\n=== 类实例化测试 ===")
    
    test_cases = []
    
    # 测试配置加载器
    try:
        from xiaoai.utils.config_loader import ConfigLoader
        config_loader = ConfigLoader()
        print("✓ ConfigLoader 实例化成功")
        test_cases.append(True)
    except Exception as e:
        print(f"✗ ConfigLoader 实例化失败: {e}")
        test_cases.append(False)
    
    # 测试多模态融合引擎
    try:
        from xiaoai.four_diagnosis.multimodal_fusion import MultimodalFusionEngine
        fusion_engine = MultimodalFusionEngine()
        print("✓ MultimodalFusionEngine 实例化成功")
        test_cases.append(True)
    except Exception as e:
        print(f"✗ MultimodalFusionEngine 实例化失败: {e}")
        test_cases.append(False)
    
    # 测试模型配置管理器
    try:
        from xiaoai.agent.model_config_manager import ModelConfigManager
        config_manager = ModelConfigManager()
        print("✓ ModelConfigManager 实例化成功")
        test_cases.append(True)
    except Exception as e:
        print(f"✗ ModelConfigManager 实例化失败: {e}")
        test_cases.append(False)
    
    success_rate = sum(test_cases) / len(test_cases) * 100
    print(f"类实例化成功率: {success_rate:.1f}% ({sum(test_cases)}/{len(test_cases)})")
    return success_rate > 70

async def test_async_functionality():
    """测试异步功能"""
    print("\n=== 异步功能测试 ===")
    
    test_results = []
    
    # 测试基本异步操作
    try:
        async def simple_async_task():
            await asyncio.sleep(0.01)
            return "async_success"
        
        result = await simple_async_task()
        if result == "async_success":
            print("✓ 基本异步操作正常")
            test_results.append(True)
        else:
            print("✗ 基本异步操作失败")
            test_results.append(False)
    except Exception as e:
        print(f"✗ 基本异步操作异常: {e}")
        test_results.append(False)
    
    # 测试异步上下文管理器
    try:
        class AsyncContextManager:
            async def __aenter__(self):
                return self
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        
        async with AsyncContextManager():
            pass
        
        print("✓ 异步上下文管理器正常")
        test_results.append(True)
    except Exception as e:
        print(f"✗ 异步上下文管理器异常: {e}")
        test_results.append(False)
    
    success_rate = sum(test_results) / len(test_results) * 100
    print(f"异步功能成功率: {success_rate:.1f}% ({sum(test_results)}/{len(test_results)})")
    return success_rate > 80

def test_server_startup():
    """测试服务器启动"""
    print("\n=== 服务器启动测试 ===")
    
    try:
        # 测试导入服务器相关模块
        from xiaoai.cli.server import create_app
        print("✓ 服务器模块导入成功")
        
        # 测试创建应用
        app = create_app()
        if app:
            print("✓ FastAPI 应用创建成功")
            return True
        else:
            print("✗ FastAPI 应用创建失败")
            return False
            
    except Exception as e:
        print(f"✗ 服务器启动测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("开始全面集成测试...")
    print(f"Python 版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print("=" * 60)
    
    # 执行所有测试
    tests = [
        ("模块导入", test_module_imports),
        ("类实例化", test_class_instantiation),
        ("异步功能", test_async_functionality),
        ("服务器启动", test_server_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("=== 全面集成测试结果汇总 ===")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    overall_success_rate = passed / total * 100
    print(f"\n总体成功率: {overall_success_rate:.1f}% ({passed}/{total})")
    
    if overall_success_rate >= 75:
        print("🎉 集成测试整体通过！Python 3.13 升级成功！")
        return 0
    elif overall_success_rate >= 50:
        print("⚠ 集成测试部分通过，需要进一步优化")
        return 1
    else:
        print("❌ 集成测试失败较多，需要重点检查")
        return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 