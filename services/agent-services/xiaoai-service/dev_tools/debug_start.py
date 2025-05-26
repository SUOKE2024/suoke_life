#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试启动脚本
"""

import sys
import os

# 添加项目根目录到PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

def test_config():
    """测试配置加载"""
    print("🔍 测试配置加载...")
    
    try:
        from pkg.utils.config_loader import get_config
        
        # 加载配置
        config = get_config("config/dev.yaml")
        print(f"✓ 配置类型: {type(config)}")
        print(f"✓ 配置路径: {config.config_path}")
        
        # 测试 get_section
        service_config = config.get_section('service')
        print(f"✓ 服务配置: {service_config}")
        
        # 测试 get_nested
        max_workers = config.get_nested('performance', 'max_workers', default=10)
        print(f"✓ 最大工作线程: {max_workers}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """测试关键导入"""
    print("\n🔍 测试关键导入...")
    
    try:
        from internal.agent.model_factory import get_model_factory
        print("✓ model_factory 导入成功")
        
        from pkg.utils.metrics import get_metrics_collector
        print("✓ metrics 导入成功")
        
        from internal.delivery.xiaoai_service_impl import XiaoAIServiceImpl
        print("✓ XiaoAIServiceImpl 导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始调试测试\n")
    
    # 测试配置
    config_ok = test_config()
    
    # 测试导入
    import_ok = test_imports()
    
    print(f"\n📊 测试结果:")
    print(f"  配置加载: {'✓' if config_ok else '❌'}")
    print(f"  关键导入: {'✓' if import_ok else '❌'}")
    
    if config_ok and import_ok:
        print("\n🎉 基础测试通过，可以尝试启动服务")
        return True
    else:
        print("\n⚠️ 存在问题，需要修复")
        return False

if __name__ == '__main__':
    main() 