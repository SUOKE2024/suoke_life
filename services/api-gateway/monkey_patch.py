import asyncio

# 添加兼容层以支持旧代码
if not hasattr(asyncio, 'coroutine'):
    def coroutine(func):
        # 创建一个简单的包装函数
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    
    # 添加coroutine属性到asyncio模块
    asyncio.coroutine = coroutine 