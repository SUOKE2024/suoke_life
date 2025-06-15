#!/usr/bin/env python3
"""
Look Service 启动脚本
用于快速启动和测试服务
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def main():
    """主函数"""
    try:
        print("🚀 启动 Look Service...")
        
        # 导入应用
        from look_service.api.app import create_app
        from look_service.core.config import settings
        
        # 创建应用
        app = create_app()
        
        print(f"✅ 应用创建成功")
        print(f"📍 服务地址: http://{settings.service.host}:{settings.service.port}")
        print(f"📚 API文档: http://{settings.service.host}:{settings.service.port}/docs")
        print(f"🔍 健康检查: http://{settings.service.host}:{settings.service.port}/health")
        
        # 如果是开发环境，启动服务器
        if settings.service.environment == "development":
            import uvicorn
            
            print("\n🔥 启动开发服务器...")
            uvicorn.run(
                "look_service.api.app:create_app",
                factory=True,
                host=settings.service.host,
                port=settings.service.port,
                reload=True,
                log_level=settings.monitoring.log_level.lower(),
            )
        else:
            print("\n💡 生产环境请使用: uvicorn look_service.api.app:create_app --factory")
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 