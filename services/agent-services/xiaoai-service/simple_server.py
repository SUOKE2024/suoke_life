#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾服务简化启动脚本
用于测试基本功能
"""

import sys
import os
import asyncio
import logging
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置基本日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_basic_imports():
    """测试基本导入"""
    logger.info("测试基本模块导入...")
    
    try:
        import xiaoai
        logger.info("✅ xiaoai 主包导入成功")
    except Exception as e:
        logger.error(f"❌ xiaoai 导入失败: {e}")
        return False
    
    try:
        from xiaoai.utils.config_loader import ConfigLoader
        config = ConfigLoader()
        logger.info("✅ ConfigLoader 创建成功")
    except Exception as e:
        logger.error(f"❌ ConfigLoader 失败: {e}")
        return False
    
    try:
        from xiaoai.agent.model_config_manager import ModelConfigManager
        manager = ModelConfigManager()
        logger.info("✅ ModelConfigManager 创建成功")
    except Exception as e:
        logger.error(f"❌ ModelConfigManager 失败: {e}")
        return False
    
    return True

async def start_basic_test_server():
    """启动基本测试服务器"""
    from aiohttp import web, web_runner
    import time
    
    async def health_check(request):
        return web.json_response({
            "status": "healthy",
            "service": "xiaoai-service",
            "version": "1.0.0",
            "timestamp": str(time.time()),
            "python_version": sys.version
        })
    
    async def chat(request):
        try:
            data = await request.json()
            message = data.get("message", "")
            
            # 简单的回复逻辑
            response = f"小艾收到您的消息: {message}。我是您的健康助手，很高兴为您服务！"
            
            return web.json_response({
                "response": response,
                "timestamp": str(time.time()),
                "status": "success"
            })
        except Exception as e:
            logger.error(f"处理聊天请求失败: {e}")
            return web.json_response({
                "error": str(e),
                "status": "error"
            }, status=500)
    
    async def root_handler(request):
        return web.json_response({
            "message": "小艾服务运行中",
            "service": "xiaoai-service",
            "version": "1.0.0",
            "endpoints": {
                "health": "GET /health",
                "chat": "POST /chat",
                "root": "GET /"
            }
        })
    
    # 创建应用
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_post('/chat', chat)
    app.router.add_get('/', root_handler)
    
    # 启动服务器
    runner = web_runner.AppRunner(app)
    await runner.setup()
    
    # 使用端口8083避免冲突
    site = web_runner.TCPSite(runner, '0.0.0.0', 8083)
    await site.start()
    
    logger.info("🚀 基本测试服务器已启动在 http://0.0.0.0:8083")
    logger.info("可用端点:")
    logger.info("  GET  /health - 健康检查")
    logger.info("  POST /chat   - 聊天接口")
    logger.info("  GET  /       - 根路径")
    logger.info("按 Ctrl+C 停止服务")
    
    # 保持服务器运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到停止信号，关闭服务器...")
        await runner.cleanup()

async def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("🤖 小艾智能体服务启动")
    logger.info("=" * 60)
    
    # 测试基本导入
    if not await test_basic_imports():
        logger.error("基本导入测试失败，退出")
        return 1
    
    logger.info("基本导入测试通过，启动服务器...")
    
    try:
        await start_basic_test_server()
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器运行异常: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0) 