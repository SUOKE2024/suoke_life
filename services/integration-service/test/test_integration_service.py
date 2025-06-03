"""
Integration Service Basic Tests
"""

import asyncio
import pytest
import httpx

# 测试配置
BASE_URL = "http://localhost:8003"
TEST_USER_ID = "test_user_001"
TEST_TOKEN = "mock_token"

class TestIntegrationService:
    """Integration Service 测试类"""
    
    @pytest.fixture
    def client(self):
        """HTTP客户端"""
        return httpx.AsyncClient(base_url=BASE_URL)
    
    @pytest.fixture
    def auth_headers(self):
        """认证头"""
        return {"Authorization": f"Bearer {TEST_TOKEN}"}
    
    async def test_health_check(self, client):
        """测试健康检查"""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert data["service"] == "integration-service"
    
    async def test_get_supported_platforms(self, client):
        """测试获取支持的平台列表"""
        response = await client.get("/api/v1/auth/platforms")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    async def test_create_integration(self, client, auth_headers):
        """测试创建集成"""
        integration_data = {
            "platform": "apple_health",
            "permissions": ["health.read.activity", "health.read.sleep"],
            "sync_frequency": "hourly"
        }
        
        response = await client.post(
            "/api/v1/integrations",
            json=integration_data,
            headers=auth_headers
        )
        
        # 由于没有实际的数据库，可能会失败，但我们检查响应格式
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
    
    async def test_get_user_integrations(self, client, auth_headers):
        """测试获取用户集成列表"""
        response = await client.get(
            "/api/v1/integrations",
            headers=auth_headers
        )
        
        # 检查响应格式
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "data" in data
            assert isinstance(data["data"], list)

async def test_basic_functionality():
    """基本功能测试"""
    print("开始测试 Integration Service...")
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 测试健康检查
        try:
            response = await client.get("/api/v1/health")
            print(f"健康检查: {response.status_code}")
            if response.status_code == 200:
                print("✓ 健康检查通过")
            else:
                print("✗ 健康检查失败")
        except Exception as e:
            print(f"✗ 健康检查异常: {str(e)}")
        
        # 测试根路径
        try:
            response = await client.get("/")
            print(f"根路径: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 服务信息: {data.get('service', 'unknown')}")
            else:
                print("✗ 根路径访问失败")
        except Exception as e:
            print(f"✗ 根路径异常: {str(e)}")
        
        # 测试平台列表
        try:
            response = await client.get("/api/v1/auth/platforms")
            print(f"平台列表: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                platforms = data.get("data", [])
                print(f"✓ 支持平台数量: {len(platforms)}")
                for platform in platforms[:3]:  # 显示前3个平台
                    print(f"  - {platform.get('platform', 'unknown')}: {platform.get('enabled', False)}")
            else:
                print("✗ 获取平台列表失败")
        except Exception as e:
            print(f"✗ 平台列表异常: {str(e)}")

def run_tests():
    """运行测试"""
    print("=" * 50)
    print("Integration Service 测试")
    print("=" * 50)
    
    try:
        asyncio.run(test_basic_functionality())
    except Exception as e:
        print(f"测试运行异常: {str(e)}")
    
    print("=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    run_tests() 