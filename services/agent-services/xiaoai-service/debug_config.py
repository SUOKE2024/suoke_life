#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置调试脚本
"""

import sys
import os

# 添加项目根目录到PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

def debug_config():
    """调试配置加载过程"""
    print("🔍 开始调试配置加载过程...\n")
    
    try:
        # 1. 测试直接导入
        print("1. 测试配置加载器导入...")
        from pkg.utils.config_loader import get_config, ConfigLoader
        print("✓ 配置加载器导入成功")
        
        # 2. 测试配置文件存在性
        print("\n2. 检查配置文件...")
        config_path = "config/dev.yaml"
        if os.path.exists(config_path):
            print(f"✓ 配置文件存在: {config_path}")
        else:
            print(f"❌ 配置文件不存在: {config_path}")
            return False
        
        # 3. 测试直接创建 ConfigLoader
        print("\n3. 测试直接创建 ConfigLoader...")
        loader = ConfigLoader(config_path)
        print(f"✓ ConfigLoader 类型: {type(loader)}")
        print(f"✓ 配置路径: {loader.config_path}")
        print(f"✓ 配置数据类型: {type(loader.config)}")
        
        # 4. 测试方法调用
        print("\n4. 测试方法调用...")
        service_config = loader.get_section('service')
        print(f"✓ get_section 返回类型: {type(service_config)}")
        print(f"✓ 服务配置: {service_config}")
        
        max_workers = loader.get_nested('performance', 'max_workers', default=10)
        print(f"✓ get_nested 返回: {max_workers}")
        
        # 5. 测试 get_config 函数
        print("\n5. 测试 get_config 函数...")
        config_instance = get_config(config_path)
        print(f"✓ get_config 返回类型: {type(config_instance)}")
        print(f"✓ 是否为 ConfigLoader 实例: {isinstance(config_instance, ConfigLoader)}")
        
        # 6. 测试多次调用 get_config
        print("\n6. 测试多次调用 get_config...")
        config_instance2 = get_config()
        print(f"✓ 第二次调用返回类型: {type(config_instance2)}")
        print(f"✓ 两次调用是否为同一实例: {config_instance is config_instance2}")
        
        # 7. 模拟 server.py 中的使用
        print("\n7. 模拟 server.py 中的使用...")
        config = get_config(config_path)
        print(f"✓ 配置对象类型: {type(config)}")
        
        # 检查是否有 get_nested 方法
        if hasattr(config, 'get_nested'):
            print("✓ 配置对象有 get_nested 方法")
            max_workers = config.get_nested('performance', 'max_workers', default=10)
            print(f"✓ max_workers: {max_workers}")
        else:
            print("❌ 配置对象没有 get_nested 方法")
            print(f"配置对象的方法: {dir(config)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_config() 