import asyncmy
import os
from ..config.settings import Settings

async def create_test_database():
    """创建测试数据库"""
    settings = Settings()
    
    # 创建连接
    conn = await asyncmy.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USERNAME,
        password=settings.DB_PASSWORD
    )
    
    try:
        # 创建测试数据库
        async with conn.cursor() as cursor:
            await cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {settings.DB_DATABASE}_test"
            )
            print(f"测试数据库 {settings.DB_DATABASE}_test 创建成功")
    
    except Exception as e:
        print(f"创建测试数据库失败: {e}")
    
    finally:
        await conn.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_test_database()) 