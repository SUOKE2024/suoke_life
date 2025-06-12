#!/usr/bin/env python3
"""
老克智能体服务异步启动测试

这个脚本测试服务的基本功能是否正常工作：
1. 模块导入
2. 配置加载
3. 智能体创建
4. API应用创建
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["SERVICE__ENVIRONMENT"] = "development"
# os.environ["SERVICE__DEBUG"] = "true"  # 测试环境可选
os.environ["MODELS__API_KEY"] = "sk-test-key-for-development"

def test_imports():
    """测试模块导入"""
    print("📦 测试模块导入...")
    
    try:
        # 测试FastAPI相关导入
        import fastapi
        import uvicorn
        import pydantic
        print("✅ FastAPI相关依赖导入成功")
        
        # 测试日志和配置导入
        import loguru
        import yaml
        print("✅ 日志和配置依赖导入成功")
        
        # 测试AI和HTTP导入
        import openai
        import httpx
        print("✅ AI和HTTP依赖导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config():
    """测试配置加载"""
    print("⚙️  测试配置加载...")
    
    try:
        from laoke_service.core.config import get_config
        config = get_config()
        print(f"✅ 配置加载成功: {config.service.name}")
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

async def test_agent():
    """测试智能体创建"""
    print("🤖 测试智能体创建...")
    
    try:
        from laoke_service.core.agent import get_agent
        agent = get_agent()
        
        # 测试创建会话
        session_id = await agent.create_session("test_user")
        print(f"✅ 智能体创建成功，会话ID: {session_id}")
        
        # 清理会话
        await agent.terminate_session(session_id)
        return True
        
    except Exception as e:
        print(f"❌ 智能体创建失败: {e}")
        return False

def test_api():
    """测试API创建"""
    print("🔗 测试API创建...")
    
    try:
        from laoke_service.api.routes import app
        print(f"✅ API应用创建成功")
        return True
        
    except Exception as e:
        print(f"❌ API应用创建失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 老克智能体服务异步启动测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        ("模块导入", test_imports()),
        ("配置加载", test_config()),
        ("智能体创建", await test_agent()),
        ("API创建", test_api()),
    ]
    
    # 统计结果
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed==total:
        print("✅ 所有测试通过！服务启动正常")
        return True
    else:
        print("❌ 部分测试失败，请检查依赖和配置")
        return False

if __name__=="__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
