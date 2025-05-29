#!/usr/bin/env python3
"""
测试服务器初始化过程
"""

import sys
from pathlib import Path

# 添加项目根目录到PYTHONPATH
sys.path.insert(0, Path().resolve())

def test_server_init():
    """测试服务器初始化过程"""
    print("🔍 测试服务器初始化过程...\n")

    try:
        # 1. 导入必要的模块
        print("1. 导入模块...")
        from pkg.utils.config_loader import get_config
        from pkg.utils.metrics import get_metrics_collector
        print("✓ 模块导入成功")

        # 2. 模拟 XiaoAIServer.__init__ 过程
        print("\n2. 模拟服务器初始化...")
        config_path = "config/dev.yaml"

        # 加载配置
        config = get_config(config_path)
        print(f"✓ 配置加载成功,类型: {type(config)}")

        # 检查配置对象的方法
        print(f"✓ 配置对象有 get_section 方法: {hasattr(config, 'get_section')}")
        print(f"✓ 配置对象有 get_nested 方法: {hasattr(config, 'get_nested')}")

        # 获取服务配置
        service_config = config.get_section('service')
        print(f"✓ 服务配置获取成功: {type(service_config)}")

        host = service_config.get('host', '0.0.0.0')
        port = service_config.get('port', 50053)
        print(f"✓ 主机: {host}, 端口: {port}")

        # 这是出错的地方
        print("\n3. 测试 get_nested 调用...")
        print(f"配置对象类型: {type(config)}")
        print(f"配置对象 ID: {id(config)}")

        max_workers = config.get_nested('performance', 'max_workers', default=10)
        print(f"✓ max_workers: {max_workers}")

        # 获取指标收集器
        metrics = get_metrics_collector()
        print(f"✓ 指标收集器获取成功: {type(metrics)}")

        print("\n🎉 服务器初始化测试成功!")
        return True

    except Exception as e:
        print(f"❌ 服务器初始化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_xiaoai_service_impl():
    """测试 XiaoAIServiceImpl 初始化"""
    print("\n🔍 测试 XiaoAIServiceImpl 初始化...\n")

    try:
        from internal.delivery.xiaoai_service_impl import XiaoAIServiceImpl

        print("正在创建 XiaoAIServiceImpl 实例...")
        service_impl = XiaoAIServiceImpl()
        print(f"✓ XiaoAIServiceImpl 创建成功: {type(service_impl)}")

        return True

    except Exception as e:
        print(f"❌ XiaoAIServiceImpl 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success1 = test_server_init()
    success2 = test_xiaoai_service_impl()

    if success1 and success2:
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠️ 存在问题需要修复")
