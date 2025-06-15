"""
API端点集成测试
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


class TestAuthEndpoints:
    """认证端点测试"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, sample_user_data):
        """测试用户注册成功"""
        with patch('soer_service.services.auth_service.AuthService.register_user') as mock_register:
            mock_register.return_value = {
                "success": True,
                "user_id": "test_user_id",
                "access_token": "test_token",
                "message": "注册成功"
            }
            
            response = await client.post("/auth/register", json=sample_user_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            assert "access_token" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_user(self, client: AsyncClient, sample_user_data):
        """测试重复用户注册"""
        with patch('soer_service.services.auth_service.AuthService.register_user') as mock_register:
            mock_register.return_value = {
                "success": False,
                "message": "用户名已存在"
            }
            
            response = await client.post("/auth/register", json=sample_user_data)
            
            assert response.status_code == 400
            data = response.json()
            assert data["success"] is False

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """测试用户登录成功"""
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        with patch('soer_service.services.auth_service.AuthService.login_user') as mock_login:
            mock_login.return_value = {
                "success": True,
                "access_token": "test_token",
                "refresh_token": "test_refresh_token",
                "user": {
                    "user_id": "test_user_id",
                    "username": "testuser",
                    "email": "test@example.com"
                }
            }
            
            response = await client.post("/auth/login", json=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """测试无效凭据登录"""
        login_data = {
            "username": "wronguser",
            "password": "wrongpassword"
        }
        
        with patch('soer_service.services.auth_service.AuthService.login_user') as mock_login:
            mock_login.return_value = {
                "success": False,
                "message": "用户名或密码错误"
            }
            
            response = await client.post("/auth/login", json=login_data)
            
            assert response.status_code == 401
            data = response.json()
            assert data["success"] is False


class TestAgentEndpoints:
    """智能体端点测试"""

    @pytest.mark.asyncio
    async def test_chat_success(self, client: AsyncClient, jwt_token):
        """测试聊天成功"""
        chat_data = {
            "message": "你好，我想了解健康建议",
            "context": {}
        }
        
        with patch('soer_service.services.agent_service.AgentService.process_message') as mock_process:
            mock_process.return_value = {
                "response": "你好！我是索儿，很高兴为您提供健康建议。",
                "intent": "greeting",
                "confidence": 0.95,
                "suggestions": ["询问具体健康问题", "查看健康数据"]
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.post("/agent/chat", json=chat_data, headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "intent" in data

    @pytest.mark.asyncio
    async def test_chat_unauthorized(self, client: AsyncClient):
        """测试未授权聊天"""
        chat_data = {
            "message": "你好",
            "context": {}
        }
        
        response = await client.post("/agent/chat", json=chat_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_capabilities(self, client: AsyncClient, jwt_token):
        """测试获取智能体能力"""
        with patch('soer_service.services.agent_service.AgentService.get_capabilities') as mock_capabilities:
            mock_capabilities.return_value = {
                "capabilities": [
                    "健康数据分析",
                    "营养建议",
                    "运动计划",
                    "睡眠分析"
                ],
                "supported_languages": ["zh-CN", "en-US"],
                "version": "1.0.0"
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.get("/agent/capabilities", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "capabilities" in data


class TestHealthEndpoints:
    """健康端点测试"""

    @pytest.mark.asyncio
    async def test_submit_health_data(self, client: AsyncClient, jwt_token, sample_health_data):
        """测试提交健康数据"""
        with patch('soer_service.services.health_service.HealthService.submit_health_data') as mock_submit:
            mock_submit.return_value = {
                "data_id": "test_data_id",
                "user_id": "test_user_id",
                "timestamp": "2024-01-01T00:00:00",
                **sample_health_data
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.post("/health/data", json=sample_health_data, headers=headers)
            
            assert response.status_code == 201
            data = response.json()
            assert "data_id" in data

    @pytest.mark.asyncio
    async def test_get_health_dashboard(self, client: AsyncClient, jwt_token):
        """测试获取健康仪表板"""
        with patch('soer_service.services.health_service.HealthService.get_health_dashboard') as mock_dashboard:
            mock_dashboard.return_value = {
                "user_id": "test_user_id",
                "health_score": 85.5,
                "latest_metrics": {
                    "heart_rate": 72,
                    "blood_pressure": "120/80"
                },
                "trends": {},
                "recommendations": []
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.get("/health/dashboard", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "health_score" in data

    @pytest.mark.asyncio
    async def test_analyze_health_data(self, client: AsyncClient, jwt_token):
        """测试健康数据分析"""
        with patch('soer_service.services.health_service.HealthService.analyze_health_data') as mock_analyze:
            mock_analyze.return_value = {
                "analysis_id": "test_analysis_id",
                "user_id": "test_user_id",
                "analysis_type": "comprehensive",
                "overall_score": 85.5,
                "category_scores": {
                    "cardiovascular": 90,
                    "metabolic": 80
                },
                "key_findings": ["心率正常", "血压稍高"],
                "recommendations": ["增加有氧运动", "减少钠摄入"]
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.post("/health/analyze", 
                                       json={"analysis_type": "comprehensive"}, 
                                       headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis_id" in data
            assert "overall_score" in data


class TestNutritionEndpoints:
    """营养端点测试"""

    @pytest.mark.asyncio
    async def test_analyze_food(self, client: AsyncClient, jwt_token, sample_nutrition_data):
        """测试食物分析"""
        with patch('soer_service.services.nutrition_service.NutritionService.analyze_food') as mock_analyze:
            mock_analyze.return_value = {
                "analysis_id": "test_analysis_id",
                "user_id": "test_user_id",
                "food_items": sample_nutrition_data["foods"],
                "total_nutrition": {
                    "calories": 250,
                    "protein": 25,
                    "carbohydrates": 30,
                    "fat": 5
                },
                "nutritional_score": 85.0,
                "recommendations": ["营养搭配良好"]
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.post("/nutrition/analyze", 
                                       json=sample_nutrition_data, 
                                       headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis_id" in data
            assert "total_nutrition" in data

    @pytest.mark.asyncio
    async def test_search_food_database(self, client: AsyncClient, jwt_token):
        """测试食物数据库搜索"""
        with patch('soer_service.services.nutrition_service.NutritionService.search_food_database') as mock_search:
            mock_search.return_value = [
                {
                    "food_id": "apple_001",
                    "name": "苹果",
                    "category": "水果",
                    "nutrition": {
                        "calories": 52,
                        "protein": 0.3,
                        "carbohydrates": 14
                    }
                }
            ]
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.get("/nutrition/search?query=苹果", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

    @pytest.mark.asyncio
    async def test_create_diet_plan(self, client: AsyncClient, jwt_token):
        """测试创建膳食计划"""
        plan_data = {
            "goals": {
                "target": "weight_loss",
                "duration_days": 7
            },
            "preferences": {
                "dietary_restrictions": ["vegetarian"],
                "disliked_foods": ["mushrooms"]
            }
        }
        
        with patch('soer_service.services.nutrition_service.NutritionService.create_diet_plan') as mock_create:
            mock_create.return_value = {
                "plan_id": "test_plan_id",
                "user_id": "test_user_id",
                "plan_name": "个性化膳食计划",
                "duration_days": 7,
                "meal_plans": []
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.post("/nutrition/diet-plan", 
                                       json=plan_data, 
                                       headers=headers)
            
            assert response.status_code == 201
            data = response.json()
            assert "plan_id" in data


class TestLifestyleEndpoints:
    """生活方式端点测试"""

    @pytest.mark.asyncio
    async def test_create_exercise_plan(self, client: AsyncClient, jwt_token, sample_exercise_goals):
        """测试创建运动计划"""
        plan_data = {
            "goals": sample_exercise_goals,
            "preferences": {
                "workout_time": "morning",
                "equipment": ["dumbbells", "resistance_bands"]
            }
        }
        
        with patch('soer_service.services.lifestyle_service.LifestyleService.create_exercise_plan') as mock_create:
            mock_create.return_value = {
                "plan_id": "test_plan_id",
                "user_id": "test_user_id",
                "plan_name": "个性化运动计划",
                "goal_type": "weight_loss",
                "duration_weeks": 12,
                "weekly_schedule": []
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.post("/lifestyle/exercise-plan", 
                                       json=plan_data, 
                                       headers=headers)
            
            assert response.status_code == 201
            data = response.json()
            assert "plan_id" in data

    @pytest.mark.asyncio
    async def test_analyze_sleep(self, client: AsyncClient, jwt_token):
        """测试睡眠分析"""
        sleep_data = {
            "date": "2024-01-01",
            "duration": 8.0,
            "efficiency": 85,
            "deep_sleep_percentage": 20,
            "rem_sleep_percentage": 25,
            "wake_up_count": 2
        }
        
        with patch('soer_service.services.lifestyle_service.LifestyleService.analyze_sleep_data') as mock_analyze:
            mock_analyze.return_value = {
                "analysis_id": "test_analysis_id",
                "user_id": "test_user_id",
                "sleep_quality_score": 85.0,
                "recommendations": ["保持规律作息"]
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.post("/lifestyle/sleep/analyze", 
                                       json=sleep_data, 
                                       headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis_id" in data

    @pytest.mark.asyncio
    async def test_assess_stress(self, client: AsyncClient, jwt_token, sample_stress_assessment):
        """测试压力评估"""
        with patch('soer_service.services.lifestyle_service.LifestyleService.assess_stress_level') as mock_assess:
            mock_assess.return_value = {
                "assessment_id": "test_assessment_id",
                "user_id": "test_user_id",
                "stress_level": "moderate",
                "stress_score": 45.0,
                "management_recommendations": ["深呼吸练习", "规律运动"]
            }
            
            headers = {"Authorization": f"Bearer {jwt_token}"}
            response = await client.post("/lifestyle/stress/assess", 
                                       json=sample_stress_assessment, 
                                       headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "assessment_id" in data
            assert "stress_level" in data


class TestHealthCheck:
    """健康检查端点测试"""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查端点"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data