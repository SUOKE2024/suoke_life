#!/usr/bin/env python3
"""
统一健康数据服务主入口
整合健康数据服务和数据库服务的统一管理器
"""

import asyncio
import signal
import sys
import logging
from unified_health_data_service import UnifiedHealthDataService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('unified_health_data_service.log')
    ]
)

logger = logging.getLogger(__name__)

class UnifiedHealthDataServiceManager:
    """
    统一健康数据服务管理器
    负责服务的启动、停止和生命周期管理
    """
    
    def __init__(self):
        """初始化服务管理器"""
        self.service = UnifiedHealthDataService()
        self.running = False
        self.shutdown_event = asyncio.Event()
        
    async def start_services(self) -> None:
        """启动所有服务"""
        try:
            logger.info("🚀 启动统一健康数据服务...")
            
            # 启动统一服务
            await self.service.start()
            
            self.running = True
            logger.info("✅ 统一健康数据服务启动成功")
            
            # 输出服务状态
            status = self.service.get_health_status()
            logger.info(f"📊 服务状态: {status}")
            
        except Exception as e:
            logger.error(f"❌ 服务启动失败: {e}")
            raise
    
    async def stop_services(self) -> None:
        """停止所有服务"""
        if not self.running:
            return
            
        logger.info("🛑 正在停止统一健康数据服务...")
        self.running = False
        
        try:
            # 停止统一服务
            await self.service.stop()
            logger.info("✅ 统一健康数据服务停止完成")
            
        except Exception as e:
            logger.error(f"❌ 服务停止时发生错误: {e}")
        
        # 设置关闭事件
        self.shutdown_event.set()
    
    def setup_signal_handlers(self) -> None:
        """设置信号处理器"""
        def signal_handler(signum, frame):
            logger.info(f"📡 接收到信号 {signum}，开始优雅关闭...")
            asyncio.create_task(self.stop_services())
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, signal_handler)
    
    async def health_check_loop(self) -> None:
        """健康检查循环"""
        while self.running:
            try:
                status = self.service.get_health_status()
                
                # 检查服务状态
                if status['status']!='running':
                    logger.warning(f"⚠️  服务状态异常: {status}")
                
                # 检查组件状态
                for component, component_status in status['components'].items():
                    if component_status['status']!='running':
                        logger.warning(f"⚠️  组件 {component} 状态异常: {component_status}")
                
                # 等待下次检查
                await asyncio.sleep(30)  # 30秒检查一次
                
            except Exception as e:
                logger.error(f"❌ 健康检查失败: {e}")
                await asyncio.sleep(10)  # 出错时10秒后重试
    
    async def run(self) -> None:
        """运行服务管理器"""
        try:
            # 设置信号处理器
            self.setup_signal_handlers()
            
            # 启动服务
            await self.start_services()
            
            # 启动健康检查
            health_check_task = asyncio.create_task(self.health_check_loop())
            
            # 等待关闭信号
            await self.shutdown_event.wait()
            
            # 取消健康检查任务
            health_check_task.cancel()
            
            # 停止服务
            await self.stop_services()
            
        except KeyboardInterrupt:
            logger.info("📡 接收到键盘中断信号")
            await self.stop_services()
        except Exception as e:
            logger.error(f"❌ 服务运行时发生错误: {e}")
            await self.stop_services()
            raise

async def main():
    """主函数"""
    logger.info("🌟 索克生活 - 统一健康数据服务")
    logger.info("=" * 50)
    
    # 创建服务管理器
    manager = UnifiedHealthDataServiceManager()
    
    try:
        # 运行服务
        await manager.run()
        
    except Exception as e:
        logger.error(f"❌ 应用程序异常退出: {e}")
        sys.exit(1)
    
    logger.info("👋 统一健康数据服务已退出")

if __name__=="__main__":
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)
    
    try:
        # 运行主函数
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 用户中断，服务退出")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)