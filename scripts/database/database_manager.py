#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活 - 数据库管理脚本
Database Management Script for Suoke Life
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.database import get_database_config, ServiceDatabaseMapping
import asyncpg
import aiofiles

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.config = get_database_config()
        self.service_mapping = ServiceDatabaseMapping()
        
    async def create_databases(self):
        """创建所有数据库"""
        logger.info("🗄️ 开始创建数据库...")
        
        try:
            # 连接到PostgreSQL服务器
            conn = await asyncpg.connect(
                host=self.config.primary_host,
                port=self.config.primary_port,
                user=self.config.primary_user,
                password=self.config.primary_password,
                database='postgres'  # 连接到默认数据库
            )
            
            # 获取所有需要创建的数据库
            databases = self.service_mapping.get_all_databases()
            databases.append(self.config.primary_database)  # 添加主数据库
            
            for database in databases:
                try:
                    # 检查数据库是否存在
                    exists = await conn.fetchval(
                        "SELECT 1 FROM pg_database WHERE datname = $1", database
                    )
                    
                    if not exists:
                        # 创建数据库
                        await conn.execute(f'CREATE DATABASE "{database}"')
                        logger.info(f"✅ 创建数据库: {database}")
                    else:
                        logger.info(f"📋 数据库已存在: {database}")
                        
                except Exception as e:
                    logger.error(f"❌ 创建数据库失败 {database}: {e}")
                    
            await conn.close()
            logger.info("🎉 数据库创建完成")
            
        except Exception as e:
            logger.error(f"❌ 数据库创建失败: {e}")
            raise
    
    async def run_migrations(self):
        """运行数据库迁移"""
        logger.info("🔄 开始运行数据库迁移...")
        
        try:
            # 运行Alembic迁移
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent
            )
            
            if result.returncode == 0:
                logger.info("✅ 数据库迁移成功")
                logger.info(result.stdout)
            else:
                logger.error("❌ 数据库迁移失败")
                logger.error(result.stderr)
                raise Exception(f"Migration failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ 运行迁移失败: {e}")
            raise
    
    async def backup_database(self, database_name: str, backup_path: str = None):
        """备份数据库"""
        if not backup_path:
            backup_path = f"backups/{database_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        logger.info(f"💾 开始备份数据库: {database_name}")
        
        try:
            # 确保备份目录存在
            Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 使用pg_dump备份
            cmd = [
                "pg_dump",
                f"--host={self.config.primary_host}",
                f"--port={self.config.primary_port}",
                f"--username={self.config.primary_user}",
                f"--dbname={database_name}",
                f"--file={backup_path}",
                "--verbose",
                "--no-password"
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config.primary_password
            
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                logger.info(f"✅ 数据库备份成功: {backup_path}")
                return backup_path
            else:
                logger.error(f"❌ 数据库备份失败: {result.stderr}")
                raise Exception(f"Backup failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ 备份数据库失败: {e}")
            raise
    
    async def restore_database(self, database_name: str, backup_path: str):
        """恢复数据库"""
        logger.info(f"🔄 开始恢复数据库: {database_name}")
        
        try:
            # 使用psql恢复
            cmd = [
                "psql",
                f"--host={self.config.primary_host}",
                f"--port={self.config.primary_port}",
                f"--username={self.config.primary_user}",
                f"--dbname={database_name}",
                f"--file={backup_path}",
                "--quiet"
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config.primary_password
            
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                logger.info(f"✅ 数据库恢复成功: {database_name}")
            else:
                logger.error(f"❌ 数据库恢复失败: {result.stderr}")
                raise Exception(f"Restore failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ 恢复数据库失败: {e}")
            raise
    
    async def check_database_health(self):
        """检查数据库健康状态"""
        logger.info("🔍 检查数据库健康状态...")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "databases": {},
            "overall_status": "healthy"
        }
        
        databases = self.service_mapping.get_all_databases()
        databases.append(self.config.primary_database)
        
        for database in databases:
            try:
                conn = await asyncpg.connect(
                    host=self.config.primary_host,
                    port=self.config.primary_port,
                    user=self.config.primary_user,
                    password=self.config.primary_password,
                    database=database
                )
                
                # 检查连接
                await conn.fetchval("SELECT 1")
                
                # 获取数据库大小
                size = await conn.fetchval(
                    "SELECT pg_size_pretty(pg_database_size($1))", database
                )
                
                # 获取连接数
                connections = await conn.fetchval(
                    "SELECT count(*) FROM pg_stat_activity WHERE datname = $1", database
                )
                
                health_report["databases"][database] = {
                    "status": "healthy",
                    "size": size,
                    "connections": connections
                }
                
                await conn.close()
                logger.info(f"✅ 数据库健康: {database}")
                
            except Exception as e:
                health_report["databases"][database] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_report["overall_status"] = "unhealthy"
                logger.error(f"❌ 数据库不健康: {database} - {e}")
        
        return health_report
    
    async def optimize_databases(self):
        """优化数据库"""
        logger.info("⚡ 开始优化数据库...")
        
        databases = self.service_mapping.get_all_databases()
        databases.append(self.config.primary_database)
        
        for database in databases:
            try:
                conn = await asyncpg.connect(
                    host=self.config.primary_host,
                    port=self.config.primary_port,
                    user=self.config.primary_user,
                    password=self.config.primary_password,
                    database=database
                )
                
                # 运行VACUUM ANALYZE
                await conn.execute("VACUUM ANALYZE")
                
                # 重建索引
                await conn.execute("REINDEX DATABASE CONCURRENTLY")
                
                await conn.close()
                logger.info(f"✅ 数据库优化完成: {database}")
                
            except Exception as e:
                logger.error(f"❌ 数据库优化失败: {database} - {e}")
    
    async def generate_database_report(self):
        """生成数据库报告"""
        logger.info("📊 生成数据库报告...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "host": self.config.primary_host,
                "port": self.config.primary_port,
                "databases_count": len(self.service_mapping.get_all_databases()) + 1
            },
            "health": await self.check_database_health(),
            "services": self.service_mapping.SERVICES
        }
        
        # 保存报告
        report_path = f"reports/database_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(report_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(report, indent=2, ensure_ascii=False))
        
        logger.info(f"📋 数据库报告已生成: {report_path}")
        return report

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='索克生活数据库管理工具')
    parser.add_argument('action', choices=[
        'create', 'migrate', 'backup', 'restore', 'health', 'optimize', 'report'
    ], help='执行的操作')
    parser.add_argument('--database', help='数据库名称')
    parser.add_argument('--backup-path', help='备份文件路径')
    
    args = parser.parse_args()
    
    manager = DatabaseManager()
    
    try:
        if args.action == 'create':
            await manager.create_databases()
        elif args.action == 'migrate':
            await manager.run_migrations()
        elif args.action == 'backup':
            if not args.database:
                logger.error("备份操作需要指定数据库名称")
                return
            await manager.backup_database(args.database, args.backup_path)
        elif args.action == 'restore':
            if not args.database or not args.backup_path:
                logger.error("恢复操作需要指定数据库名称和备份文件路径")
                return
            await manager.restore_database(args.database, args.backup_path)
        elif args.action == 'health':
            health = await manager.check_database_health()
            print(json.dumps(health, indent=2, ensure_ascii=False))
        elif args.action == 'optimize':
            await manager.optimize_databases()
        elif args.action == 'report':
            await manager.generate_database_report()
            
    except Exception as e:
        logger.error(f"操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 