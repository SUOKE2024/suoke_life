"""
test_integration - 索克生活项目模块
"""

        from httpx import AsyncClient
    from httpx import AsyncClient
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from health_data_service.api.main import app
from health_data_service.core.cache import cache_manager
from health_data_service.core.config import get_settings
from health_data_service.core.database import get_database
from health_data_service.core.security import security_manager
from health_data_service.models.health_data import DataType, DataSource
from health_data_service.services.health_data_service import HealthDataService
from httpx import AsyncClient
from typing import Dict, Any, List
import asyncio
import json
import pytest
import pytest_asyncio

#!/usr/bin/env python3
"""
健康数据服务集成测试

测试完整的API流程、数据处理管道、缓存、认证等功能。
"""




class TestHealthDataServiceIntegration:
    """健康数据服务集成测试"""

    @pytest_asyncio.fixture(scope="class")
    async def setup_test_environment(self):
        """设置测试环境"""
        # 在测试环境中跳过真实的数据库初始化
        yield

    @pytest_asyncio.fixture
    async def async_client(self, setup_test_environment):
        """异步HTTP客户端"""
        async with AsyncClient(base_url="http://test") as client:
            yield client

    @pytest_asyncio.fixture
    async def authenticated_client(self, async_client):
        """认证后的客户端"""
        # 创建测试用户并获取令牌
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "test_password123"
        }
        
        # 注册用户
        response = await async_client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # 登录获取令牌
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = await async_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        access_token = token_data["access_token"]
        
        # 设置认证头
        async_client.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        
        return async_client, token_data

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """测试健康检查端点"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "database" in data
        assert "cache" in data

    @pytest.mark.asyncio
    async def test_user_authentication_flow(self, async_client):
        """测试用户认证流程"""
        # 1. 注册新用户
        user_data = {
            "username": "integration_test_user",
            "email": "integration@test.com",
            "password": "SecurePassword123!",
            "full_name": "Integration Test User"
        }
        
        response = await async_client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        register_data = response.json()
        assert register_data["success"] is True
        assert "user_id" in register_data
        
        # 2. 登录
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        response = await async_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        
        # 3. 使用访问令牌访问受保护的端点
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = await async_client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_info = response.json()
        assert user_info["username"] == user_data["username"]
        assert user_info["email"] == user_data["email"]
        
        # 4. 刷新令牌
        refresh_data = {"refresh_token": token_data["refresh_token"]}
        response = await async_client.post("/auth/refresh", json=refresh_data)
        assert response.status_code == 200
        
        new_token_data = response.json()
        assert "access_token" in new_token_data
        assert new_token_data["access_token"] != token_data["access_token"]

    @pytest.mark.asyncio
    async def test_health_data_crud_operations(self, authenticated_client):
        """测试健康数据CRUD操作"""
        client, token_data = authenticated_client
        
        # 1. 创建健康数据
        health_data = {
            "user_id": 1,
            "data_type": "VITAL_SIGNS",
            "data_source": "DEVICE",
            "raw_data": {
                "heart_rate": 72,
                "blood_pressure_systolic": 120,
                "blood_pressure_diastolic": 80,
                "body_temperature": 36.5
            },
            "device_id": "DEVICE_001",
            "location": "Home",
            "tags": ["morning", "resting"],
            "recorded_at": datetime.now().isoformat()
        }
        
        response = await client.post("/health-data/", json=health_data)
        assert response.status_code == 201
        
        created_data = response.json()
        assert created_data["success"] is True
        assert "data" in created_data
        
        health_data_id = created_data["data"]["id"]
        assert health_data_id > 0
        
        # 2. 获取健康数据
        response = await client.get(f"/health-data/{health_data_id}")
        assert response.status_code == 200
        
        retrieved_data = response.json()
        assert retrieved_data["success"] is True
        assert retrieved_data["data"]["id"] == health_data_id
        assert retrieved_data["data"]["data_type"] == health_data["data_type"]
        
        # 3. 更新健康数据
        update_data = {
            "processed_data": {
                "heart_rate_zone": "normal",
                "blood_pressure_category": "normal"
            },
            "quality_score": 0.95,
            "confidence_score": 0.9,
            "is_validated": True
        }
        
        response = await client.put(f"/health-data/{health_data_id}", json=update_data)
        assert response.status_code == 200
        
        updated_data = response.json()
        assert updated_data["success"] is True
        assert updated_data["data"]["quality_score"] == update_data["quality_score"]
        assert updated_data["data"]["is_validated"] is True
        
        # 4. 列出健康数据
        response = await client.get("/health-data/")
        assert response.status_code == 200
        
        list_data = response.json()
        assert list_data["success"] is True
        assert len(list_data["items"]) >= 1
        assert list_data["total"] >= 1
        
        # 5. 删除健康数据
        response = await client.delete(f"/health-data/{health_data_id}")
        assert response.status_code == 200
        
        delete_data = response.json()
        assert delete_data["success"] is True
        
        # 6. 验证删除
        response = await client.get(f"/health-data/{health_data_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_vital_signs_operations(self, authenticated_client):
        """测试生命体征操作"""
        client, token_data = authenticated_client
        
        # 创建生命体征数据
        vital_signs_data = {
            "user_id": 1,
            "heart_rate": 75,
            "blood_pressure_systolic": 118,
            "blood_pressure_diastolic": 78,
            "body_temperature": 36.7,
            "respiratory_rate": 16,
            "oxygen_saturation": 98.5,
            "weight": 70.5,
            "height": 175.0,
            "device_id": "VITALS_MONITOR_001",
            "notes": "Morning measurement",
            "recorded_at": datetime.now().isoformat()
        }
        
        response = await client.post("/vital-signs/", json=vital_signs_data)
        assert response.status_code == 201
        
        created_data = response.json()
        assert created_data["success"] is True
        
        vital_signs_id = created_data["data"]["id"]
        
        # 获取生命体征数据
        response = await client.get(f"/vital-signs/{vital_signs_id}")
        assert response.status_code == 200
        
        retrieved_data = response.json()
        assert retrieved_data["data"]["heart_rate"] == vital_signs_data["heart_rate"]
        assert retrieved_data["data"]["bmi"] is not None  # 应该自动计算BMI

    @pytest.mark.asyncio
    async def test_data_processing_pipeline(self, authenticated_client):
        """测试数据处理管道"""
        client, token_data = authenticated_client
        
        # 创建包含异常值的健康数据
        health_data = {
            "data_type": "VITAL_SIGNS",
            "data_source": "MANUAL",
            "raw_data": {
                "heart_rate": 250,  # 异常高值
                "blood_pressure_systolic": 300,  # 异常高值
                "body_temperature": 45.0  # 异常高值
            },
            "recorded_at": datetime.now().isoformat()
        }
        
        response = await client.post("/health-data/", json=health_data)
        assert response.status_code == 201
        
        created_data = response.json()
        health_data_id = created_data["data"]["id"]
        
        # 等待数据处理完成
        await asyncio.sleep(2)
        
        # 获取处理后的数据
        response = await client.get(f"/health-data/{health_data_id}")
        assert response.status_code == 200
        
        processed_data = response.json()
        
        # 验证数据处理结果
        assert processed_data["data"]["is_anomaly"] is True
        assert processed_data["data"]["quality_score"] is not None
        assert processed_data["data"]["confidence_score"] is not None
        
        # 获取处理记录
        response = await client.get(f"/health-data/{health_data_id}/processing-records")
        assert response.status_code == 200
        
        records_data = response.json()
        assert len(records_data["items"]) > 0
        
        # 验证处理阶段
        stages = [record["stage"] for record in records_data["items"]]
        assert "validation" in stages
        assert "cleaning" in stages

    @pytest.mark.asyncio
    async def test_caching_functionality(self, authenticated_client):
        """测试缓存功能"""
        client, token_data = authenticated_client
        
        # 创建健康数据
        health_data = {
            "data_type": "VITAL_SIGNS",
            "data_source": "DEVICE",
            "raw_data": {"heart_rate": 70},
            "recorded_at": datetime.now().isoformat()
        }
        
        response = await client.post("/health-data/", json=health_data)
        assert response.status_code == 201
        
        health_data_id = response.json()["data"]["id"]
        
        # 第一次获取（应该从数据库获取）
        start_time = datetime.now()
        response = await client.get(f"/health-data/{health_data_id}")
        first_request_time = (datetime.now() - start_time).total_seconds()
        assert response.status_code == 200
        
        # 第二次获取（应该从缓存获取）
        start_time = datetime.now()
        response = await client.get(f"/health-data/{health_data_id}")
        second_request_time = (datetime.now() - start_time).total_seconds()
        assert response.status_code == 200
        
        # 缓存的请求应该更快
        assert second_request_time < first_request_time

    @pytest.mark.asyncio
    async def test_data_validation_and_error_handling(self, authenticated_client):
        """测试数据验证和错误处理"""
        client, token_data = authenticated_client
        
        # 测试无效数据类型
        invalid_data = {
            "data_type": "INVALID_TYPE",
            "data_source": "MANUAL",
            "raw_data": {"test": "data"},
            "recorded_at": datetime.now().isoformat()
        }
        
        response = await client.post("/health-data/", json=invalid_data)
        assert response.status_code == 422
        
        # 测试缺少必需字段
        incomplete_data = {
            "data_type": "VITAL_SIGNS"
            # 缺少其他必需字段
        }
        
        response = await client.post("/health-data/", json=incomplete_data)
        assert response.status_code == 422
        
        # 测试无效的数据格式
        invalid_format_data = {
            "data_type": "VITAL_SIGNS",
            "data_source": "MANUAL",
            "raw_data": "not_a_dict",  # 应该是字典
            "recorded_at": "invalid_date"  # 无效日期格式
        }
        
        response = await client.post("/health-data/", json=invalid_format_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_pagination_and_filtering(self, authenticated_client):
        """测试分页和过滤功能"""
        client, token_data = authenticated_client
        
        # 创建多个健康数据记录
        data_types = ["VITAL_SIGNS", "BLOOD_TEST", "EXERCISE"]
        created_ids = []
        
        for i, data_type in enumerate(data_types):
            health_data = {
                "data_type": data_type,
                "data_source": "MANUAL",
                "raw_data": {"test_value": i},
                "recorded_at": (datetime.now() - timedelta(days=i)).isoformat()
            }
            
            response = await client.post("/health-data/", json=health_data)
            assert response.status_code == 201
            created_ids.append(response.json()["data"]["id"])
        
        # 测试分页
        response = await client.get("/health-data/?skip=0&limit=2")
        assert response.status_code == 200
        
        page_data = response.json()
        assert len(page_data["items"]) <= 2
        assert page_data["total"] >= len(data_types)
        
        # 测试按数据类型过滤
        response = await client.get("/health-data/?data_type=VITAL_SIGNS")
        assert response.status_code == 200
        
        filtered_data = response.json()
        for item in filtered_data["items"]:
            assert item["data_type"] == "VITAL_SIGNS"
        
        # 测试日期范围过滤
        start_date = (datetime.now() - timedelta(days=1)).isoformat()
        end_date = datetime.now().isoformat()
        
        response = await client.get(f"/health-data/?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, authenticated_client):
        """测试并发操作"""
        client, token_data = authenticated_client
        
        async def create_health_data(index: int):
            """创建健康数据的异步函数"""
            health_data = {
                "data_type": "VITAL_SIGNS",
                "data_source": "DEVICE",
                "raw_data": {"heart_rate": 70 + index},
                "recorded_at": datetime.now().isoformat()
            }
            
            response = await client.post("/health-data/", json=health_data)
            return response.status_code == 201
        
        # 并发创建多个健康数据记录
        tasks = [create_health_data(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # 验证所有操作都成功
        assert all(results)
        
        # 验证数据库中的记录数
        response = await client.get("/health-data/")
        assert response.status_code == 200
        
        list_data = response.json()
        assert list_data["total"] >= 10

    @pytest.mark.asyncio
    async def test_metrics_and_monitoring(self, async_client):
        """测试指标和监控端点"""
        # 测试Prometheus指标端点
        response = await async_client.get("/metrics")
        assert response.status_code == 200
        
        metrics_text = response.text
        assert "health_data_requests_total" in metrics_text
        assert "health_data_processing_duration_seconds" in metrics_text
        
        # 测试健康检查详细信息
        response = await async_client.get("/health/detailed")
        assert response.status_code == 200
        
        health_data = response.json()
        assert "database" in health_data
        assert "cache" in health_data
        assert "pipeline" in health_data

    @pytest.mark.asyncio
    async def test_data_export_and_import(self, authenticated_client):
        """测试数据导出和导入功能"""
        client, token_data = authenticated_client
        
        # 创建一些测试数据
        health_data_list = []
        for i in range(3):
            health_data = {
                "data_type": "VITAL_SIGNS",
                "data_source": "MANUAL",
                "raw_data": {"heart_rate": 70 + i},
                "recorded_at": (datetime.now() - timedelta(hours=i)).isoformat()
            }
            
            response = await client.post("/health-data/", json=health_data)
            assert response.status_code == 201
            health_data_list.append(response.json()["data"]["id"])
        
        # 导出数据
        export_params = {
            "format": "json",
            "start_date": (datetime.now() - timedelta(days=1)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        
        response = await client.get("/health-data/export", params=export_params)
        assert response.status_code == 200
        
        exported_data = response.json()
        assert "data" in exported_data
        assert len(exported_data["data"]) >= 3

    @pytest.mark.asyncio
    async def test_error_recovery_and_resilience(self, authenticated_client):
        """测试错误恢复和系统韧性"""
        client, token_data = authenticated_client
        
        # 测试数据库连接错误恢复
        # 这里可以模拟数据库连接问题
        
        # 测试缓存失效时的降级处理
        # 暂时禁用缓存
        await cache_manager.close()
        
        # 创建健康数据（应该仍然工作，只是没有缓存）
        health_data = {
            "data_type": "VITAL_SIGNS",
            "data_source": "MANUAL",
            "raw_data": {"heart_rate": 72},
            "recorded_at": datetime.now().isoformat()
        }
        
        response = await client.post("/health-data/", json=health_data)
        assert response.status_code == 201
        
        # 重新初始化缓存
        await cache_manager.initialize()

    @pytest.mark.asyncio
    async def test_security_and_authorization(self, async_client):
        """测试安全性和授权"""
        # 测试未认证访问
        response = await async_client.get("/health-data/")
        assert response.status_code == 401
        
        # 测试无效令牌
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/health-data/", headers=headers)
        assert response.status_code == 401
        
        # 测试过期令牌
        # 这里可以创建一个过期的令牌进行测试
        
        # 测试权限控制
        # 创建不同权限级别的用户进行测试


@pytest.mark.asyncio
async def test_full_system_integration():
    """完整系统集成测试"""
    # 这个测试模拟完整的用户使用流程
    async with AsyncClient(base_url="http://test") as client:
        # 1. 用户注册
        user_data = {
            "username": "full_test_user",
            "email": "fulltest@example.com",
            "password": "FullTest123!",
            "full_name": "Full Test User"
        }
        
        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # 2. 用户登录
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # 3. 创建健康档案
        profile_data = {
            "profile_data": {
                "age": 30,
                "gender": "male",
                "height": 175,
                "weight": 70
            },
            "allergies": ["peanuts"],
            "chronic_conditions": [],
            "medications": {}
        }
        
        response = await client.post("/user-profile/", json=profile_data, headers=headers)
        assert response.status_code == 201
        
        # 4. 添加生命体征数据
        vital_signs = {
            "heart_rate": 72,
            "blood_pressure_systolic": 120,
            "blood_pressure_diastolic": 80,
            "body_temperature": 36.5,
            "weight": 70.5,
            "height": 175.0,
            "recorded_at": datetime.now().isoformat()
        }
        
        response = await client.post("/vital-signs/", json=vital_signs, headers=headers)
        assert response.status_code == 201
        
        # 5. 添加运动数据
        exercise_data = {
            "data_type": "EXERCISE",
            "data_source": "DEVICE",
            "raw_data": {
                "activity_type": "running",
                "duration_minutes": 30,
                "distance_km": 5.0,
                "calories_burned": 300,
                "average_heart_rate": 150
            },
            "device_id": "FITNESS_TRACKER_001",
            "recorded_at": datetime.now().isoformat()
        }
        
        response = await client.post("/health-data/", json=exercise_data, headers=headers)
        assert response.status_code == 201
        
        # 6. 获取健康数据摘要
        response = await client.get("/health-data/summary", headers=headers)
        assert response.status_code == 200
        
        summary_data = response.json()
        assert "vital_signs" in summary_data
        assert "exercise" in summary_data
        
        # 7. 生成健康报告
        report_params = {
            "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "include_trends": True
        }
        
        response = await client.get("/health-data/report", params=report_params, headers=headers)
        assert response.status_code == 200
        
        report_data = response.json()
        assert "summary" in report_data
        assert "trends" in report_data


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--asyncio-mode=auto"]) 