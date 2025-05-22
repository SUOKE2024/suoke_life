"""
数据库引擎和监控使用示例

本示例展示如何使用数据库引擎和监控组件，包括：
1. 初始化数据库引擎
2. 执行读写操作
3. 使用读写分离
4. 配置数据库监控
5. 使用SQLite本地存储
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional

from sqlalchemy import select, insert, update, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from db_engine import DatabaseEngine
from db_monitor import DatabaseMonitor
from sqlite_manager import SQLiteManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseExample:
    """数据库使用示例类"""
    
    def __init__(self, config_path: str):
        """
        初始化示例
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        
        # 初始化数据库引擎
        self.db_engine = DatabaseEngine(config_path)
        
        # 初始化数据库监控
        self.db_monitor = DatabaseMonitor(
            service_name="example-service",
            config={"slow_query_threshold": 500, "alert_enabled": True},
            prometheus_port=9090
        )
        
        # 初始化SQLite管理器
        self.sqlite_manager = SQLiteManager(
            db_path="./data/local.db",
            config={
                "journal_mode": "WAL",
                "synchronous": "NORMAL",
                "backup": {"enabled": True, "interval": 3600}
            }
        )
    
    async def initialize(self):
        """初始化数据库连接和监控"""
        # 启动数据库监控
        await self.db_monitor.start_monitoring(self.db_engine)
        logger.info("数据库监控已启动")
    
    async def cleanup(self):
        """清理资源"""
        # 停止数据库监控
        await self.db_monitor.stop_monitoring()
        
        # 关闭数据库连接
        await self.db_engine.close_async()
        logger.info("数据库连接已关闭")
    
    @db_monitor.track_query(operation="select", query="SELECT * FROM users WHERE id = :user_id", params={"user_id": "..."})
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息（读操作示例）
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息或None
        """
        # 使用只读连接（自动路由到副本）
        async with self.db_engine.get_read_session() as session:
            # 使用SQLAlchemy执行查询
            result = await session.execute(
                select(text("*")).select_from(text("users")).where(text("id = :user_id")),
                {"user_id": user_id}
            )
            user = result.mappings().first()
            
            if user:
                return dict(user)
            return None
    
    @db_monitor.track_query(operation="insert", query="INSERT INTO users (id, name, email) VALUES (:id, :name, :email)", params={"id": "...", "name": "...", "email": "..."})
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """
        创建用户（写操作示例）
        
        Args:
            user_data: 用户数据
            
        Returns:
            创建的用户ID
        """
        # 使用写连接（主数据库）
        async with self.db_engine.get_async_session() as session:
            # 插入用户数据
            await session.execute(
                text("INSERT INTO users (id, name, email) VALUES (:id, :name, :email)"),
                user_data
            )
            
            # 提交事务
            await session.commit()
            
            return user_data["id"]
    
    async def demonstrate_raw_query(self):
        """展示原始SQL查询执行"""
        # 执行原始SQL查询
        results = await self.db_engine.execute_query(
            query="SELECT * FROM users WHERE created_at > :date",
            params={"date": "2023-01-01"},
            is_read_query=True  # 标记为读查询，使用只读副本
        )
        
        logger.info(f"查询结果: {results}")
    
    async def demonstrate_sqlite(self):
        """展示SQLite本地存储使用"""
        # 创建表
        await self.sqlite_manager.execute_async(
            "CREATE TABLE IF NOT EXISTS local_cache (key TEXT PRIMARY KEY, value TEXT, timestamp INTEGER)"
        )
        
        # 插入数据
        await self.sqlite_manager.execute_async(
            "INSERT OR REPLACE INTO local_cache (key, value, timestamp) VALUES (?, ?, ?)",
            ("user_123", '{"name": "张三", "age": 30}', int(asyncio.get_event_loop().time()))
        )
        
        # 查询数据
        result = await self.sqlite_manager.execute_async(
            "SELECT * FROM local_cache WHERE key = ?",
            ("user_123",)
        )
        
        logger.info(f"SQLite查询结果: {result}")
        
        # 备份数据库
        backup_path = self.sqlite_manager.backup_db()
        logger.info(f"数据库已备份到: {backup_path}")
    
    async def demonstrate_health_check(self):
        """展示健康检查功能"""
        # 获取数据库健康状态
        health_status = self.db_monitor.get_health_status()
        logger.info(f"数据库健康状态: {health_status}")
        
        # 获取慢查询列表
        slow_queries = self.db_monitor.get_slow_queries(limit=5)
        logger.info(f"慢查询列表: {slow_queries}")

async def main():
    """主函数"""
    # 创建示例实例
    example = DatabaseExample("../../../services/common/db_config.yaml")
    
    try:
        # 初始化
        await example.initialize()
        
        # 执行示例操作
        user_id = "user_456"
        user_data = {
            "id": user_id,
            "name": "李四",
            "email": "lisi@example.com"
        }
        
        # 创建用户
        await example.create_user(user_data)
        logger.info(f"用户已创建: {user_id}")
        
        # 获取用户
        user = await example.get_user(user_id)
        logger.info(f"获取到用户: {user}")
        
        # 展示其他功能
        await example.demonstrate_raw_query()
        await example.demonstrate_sqlite()
        await example.demonstrate_health_check()
        
    except Exception as e:
        logger.error(f"示例执行失败: {str(e)}")
    finally:
        # 清理资源
        await example.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 