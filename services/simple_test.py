#!/usr/bin/env python3
import asyncio
import sys

async def main():
    print('🧪 索克生活微服务快速功能验证')
    print('=' * 40)
    
    # 测试用户管理服务
    try:
        sys.path.insert(0, 'user-management-service')
        from user_management_service.models import User
        user = User(id='test', username='test', email='test@test.com', password_hash='hash')
        print('✅ 用户管理服务测试通过')
    except Exception as e:
        print(f'❌ 用户管理服务测试失败: {e}')
    
    # 测试API网关
    try:
        sys.path.insert(0, 'api-gateway')
        from suoke_api_gateway.core.gateway import APIGateway
        gateway = APIGateway()
        await gateway.initialize()
        print('✅ API网关测试通过')
    except Exception as e:
        print(f'❌ API网关测试失败: {e}')
    
    # 测试小艾智能体
    try:
        sys.path.insert(0, 'agent-services/xiaoai-service')
        from xiaoai.core import XiaoaiAgent
        agent = XiaoaiAgent()
        await agent.initialize()
        response = await agent.process_message('你好')
        print(f'✅ 小艾智能体测试通过 - 响应: {response[:30]}...')
    except Exception as e:
        print(f'❌ 小艾智能体测试失败: {e}')

if __name__=="__main__":
    asyncio.run(main()) 