#!/usr/bin/env python3
"""
Soer Service 数据库迁移脚本
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

logger = logging.getLogger(__name__)

async def init_mongodb():
    """初始化MongoDB"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.soer_db
    
    # 创建集合和索引
    collections = [
        "users", "health_records", "nutrition_plans", 
        "tcm_constitutions", "lifestyle_recommendations"
    ]
    
    for collection_name in collections:
        collection = db[collection_name]
        
        # 创建基础索引
        if collection_name == "users":
            await collection.create_index("user_id", unique=True)
            await collection.create_index("email", unique=True)
        elif collection_name == "health_records":
            await collection.create_index([("user_id", 1), ("created_at", -1)])
        
        logger.info(f"Collection {collection_name} initialized")
    
    logger.info("MongoDB initialization completed")

async def init_redis():
    """初始化Redis"""
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    # 设置基础配置
    await redis_client.set("soer:config:version", "1.0.0")
    await redis_client.set("soer:config:initialized", "true")
    
    logger.info("Redis initialization completed")

async def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        await init_mongodb()
        await init_redis()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
