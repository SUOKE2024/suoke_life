#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试统一后的模型工厂
"""

import sys
import asyncio
import logging

# 添加项目路径
sys.path.append('.')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_model_factory():
    """测试模型工厂"""
    try:
        # 导入模型工厂
        from internal.agent.model_factory import get_model_factory
        
        # 创建模型工厂实例
        factory = await get_model_factory()
        
        print(f"✓ 异步模型工厂创建成功: {type(factory).__name__}")
        print(f"✓ 工厂已初始化: {factory.initialized}")
        print(f"✓ 可用模型数量: {len(factory.get_available_models())}")
        
        # 获取健康状态
        health_status = factory.get_model_health_status()
        print(f"✓ 健康状态检查完成，监控 {len(health_status)} 个模型")
        
        # 关闭工厂
        await factory.close()
        print("✓ 模型工厂已关闭")
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        return False

async def test_agent_manager():
    """测试智能体管理器"""
    try:
        from internal.agent.agent_manager import AgentManager
        
        # 创建智能体管理器
        manager = AgentManager()
        
        # 异步初始化
        await manager.initialize()
        
        print(f"✓ 智能体管理器创建成功: {type(manager).__name__}")
        print(f"✓ 模型工厂已初始化: {manager.model_factory is not None}")
        
        # 关闭管理器
        await manager.close()
        print("✓ 智能体管理器已关闭")
        
        return True
        
    except Exception as e:
        logger.error(f"智能体管理器测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("开始测试统一后的模型工厂...")
    
    # 测试模型工厂
    factory_test = await test_model_factory()
    
    # 测试智能体管理器
    manager_test = await test_agent_manager()
    
    # 输出结果
    if factory_test and manager_test:
        print("\n🎉 所有测试通过！enhanced_model_factory 已成功集成到 model_factory 中")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    asyncio.run(main()) 