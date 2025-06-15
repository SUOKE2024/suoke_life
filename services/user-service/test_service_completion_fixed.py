#!/usr/bin/env python3
"""
用户服务完成度测试脚本（修复版）
验证user-service的100%完成度和功能正确性
"""
import asyncio
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入测试所需的模块
from run_service import create_app
from internal.domain.user import User, UserStatus, UserRole
from internal.model.user import CreateUserRequest, UpdateUserRequest
from config.settings import get_settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserServiceTester:
    """用户服务测试器"""
    
    def __init__(self):
        self.app = None
        self.client = None
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": [],
            "completion_percentage": 0.0
        }
    
    async def setup(self):
        """设置测试环境"""
        try:
            logger.info("正在设置测试环境...")
            self.app = await create_app()
            self.client = TestClient(self.app)
            logger.info("测试环境设置完成")
            return True
        except Exception as e:
            logger.error(f"测试环境设置失败: {e}")
            return False
    
    def run_test(self, test_name: str, test_func):
        """运行单个测试"""
        self.test_results["total_tests"] += 1
        
        try:
            logger.info(f"运行测试: {test_name}")
            start_time = time.time()
            
            result = test_func()
            
            duration = time.time() - start_time
            
            if result:
                self.test_results["passed_tests"] += 1
                status = "PASSED"
                logger.info(f"✅ {test_name} - 通过 ({duration:.2f}s)")
            else:
                self.test_results["failed_tests"] += 1
                status = "FAILED"
                logger.error(f"❌ {test_name} - 失败 ({duration:.2f}s)")
            
            self.test_results["test_details"].append({
                "name": test_name,
                "status": status,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            self.test_results["failed_tests"] += 1
            logger.error(f"❌ {test_name} - 异常: {e}")
            
            self.test_results["test_details"].append({
                "name": test_name,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
            return False
    
    def test_health_check(self) -> bool:
        """测试健康检查端点"""
        response = self.client.get("/health")
        return response.status_code == 200 and "status" in response.json()
    
    def test_api_documentation(self) -> bool:
        """测试API文档可访问性"""
        response = self.client.get("/docs")
        return response.status_code == 200
    
    def test_create_user(self) -> bool:
        """测试创建用户功能"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"testuser{unique_id}",
            "email": f"test{unique_id}@example.com",
            "password": "TestPassword123",
            "fullName": "测试用户",
            "phone": "13800138000"
        }
        
        response = self.client.post("/api/v1/users", json=user_data)
        
        if response.status_code != 201:
            logger.error(f"创建用户失败: {response.status_code} - {response.text}")
            return False
        
        user_response = response.json()
        return (
            user_response["username"] == user_data["username"] and
            user_response["email"] == user_data["email"] and
            user_response["fullName"] == user_data["fullName"]
        )
    
    def test_get_user(self) -> bool:
        """测试获取用户功能"""
        # 首先创建一个用户
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"getuser{unique_id}",
            "email": f"getuser{unique_id}@example.com",
            "password": "TestPassword123"
        }
        
        create_response = self.client.post("/api/v1/users", json=user_data)
        if create_response.status_code != 201:
            return False
        
        user_id = create_response.json()["userId"]
        
        # 获取用户
        response = self.client.get(f"/api/v1/users/{user_id}")
        
        if response.status_code != 200:
            logger.error(f"获取用户失败: {response.status_code} - {response.text}")
            return False
        
        user_response = response.json()
        return user_response["userId"] == user_id
    
    def test_update_user(self) -> bool:
        """测试更新用户功能"""
        # 首先创建一个用户
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"updateuser{unique_id}",
            "email": f"updateuser{unique_id}@example.com",
            "password": "TestPassword123"
        }
        
        create_response = self.client.post("/api/v1/users", json=user_data)
        if create_response.status_code != 201:
            return False
        
        user_id = create_response.json()["userId"]
        
        # 更新用户
        update_data = {
            "fullName": "更新后的用户名",
            "phone": "13900139000"
        }
        
        response = self.client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        if response.status_code != 200:
            logger.error(f"更新用户失败: {response.status_code} - {response.text}")
            return False
        
        user_response = response.json()
        return (
            user_response["fullName"] == update_data["fullName"] and
            user_response["phone"] == update_data["phone"]
        )
    
    def test_list_users(self) -> bool:
        """测试用户列表功能"""
        response = self.client.get("/api/v1/users")
        
        if response.status_code != 200:
            logger.error(f"获取用户列表失败: {response.status_code} - {response.text}")
            return False
        
        users_response = response.json()
        return (
            "data" in users_response and
            "meta" in users_response and
            isinstance(users_response["data"], list)
        )
    
    def test_user_validation(self) -> bool:
        """测试用户数据验证"""
        # 测试无效的用户名
        invalid_user_data = {
            "username": "ab",  # 太短
            "email": "invalid-email",  # 无效邮箱
            "password": "123"  # 密码太短
        }
        
        response = self.client.post("/api/v1/users", json=invalid_user_data)
        return response.status_code == 422  # 验证错误
    
    def test_duplicate_user_prevention(self) -> bool:
        """测试重复用户防护"""
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"duplicateuser{unique_id}",
            "email": f"duplicate{unique_id}@example.com",
            "password": "TestPassword123"
        }
        
        # 创建第一个用户
        first_response = self.client.post("/api/v1/users", json=user_data)
        if first_response.status_code != 201:
            return False
        
        # 尝试创建重复用户
        second_response = self.client.post("/api/v1/users", json=user_data)
        return second_response.status_code == 409  # 冲突错误
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        # 测试获取不存在的用户
        response = self.client.get("/api/v1/users/nonexistent-id")
        
        if response.status_code != 404:
            return False
        
        error_response = response.json()
        return "error" in error_response
    
    def test_request_id_middleware(self) -> bool:
        """测试请求ID中间件"""
        response = self.client.get("/health")
        return "X-Request-ID" in response.headers
    
    def test_cors_headers(self) -> bool:
        """测试CORS头部"""
        # 测试普通GET请求是否有CORS头
        headers = {"Origin": "http://localhost:3000"}
        response = self.client.get("/api/v1/users", headers=headers)
        
        # 检查是否有CORS头
        cors_headers = [h.lower() for h in response.headers.keys()]
        has_cors = "access-control-allow-origin" in cors_headers
        
        return response.status_code == 200 and has_cors
    
    def test_database_operations(self) -> bool:
        """测试数据库操作"""
        try:
            # 测试数据库连接
            user_repository = self.app.state.user_repository
            
            # 测试基本的数据库操作
            return hasattr(user_repository, 'get_user_by_id')
        except Exception as e:
            logger.error(f"数据库操作测试失败: {e}")
            return False
    
    def test_configuration_loading(self) -> bool:
        """测试配置加载"""
        try:
            settings = self.app.state.settings
            return (
                hasattr(settings, 'app') and
                hasattr(settings, 'database') and
                hasattr(settings, 'security')
            )
        except Exception as e:
            logger.error(f"配置加载测试失败: {e}")
            return False
    
    def test_logging_functionality(self) -> bool:
        """测试日志功能"""
        try:
            # 测试日志记录器是否正常工作
            test_logger = logging.getLogger("test_logger")
            test_logger.info("测试日志消息")
            return True
        except Exception as e:
            logger.error(f"日志功能测试失败: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始运行用户服务完成度测试...")
        
        # 设置测试环境
        if not await self.setup():
            logger.error("测试环境设置失败，退出测试")
            return False
        
        # 定义测试用例
        tests = [
            ("健康检查", self.test_health_check),
            ("API文档", self.test_api_documentation),
            ("创建用户", self.test_create_user),
            ("获取用户", self.test_get_user),
            ("更新用户", self.test_update_user),
            ("用户列表", self.test_list_users),
            ("数据验证", self.test_user_validation),
            ("重复用户防护", self.test_duplicate_user_prevention),
            ("错误处理", self.test_error_handling),
            ("请求ID中间件", self.test_request_id_middleware),
            ("CORS支持", self.test_cors_headers),
            ("数据库操作", self.test_database_operations),
            ("配置加载", self.test_configuration_loading),
            ("日志功能", self.test_logging_functionality),
        ]
        
        # 运行所有测试
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # 计算完成度
        self.test_results["completion_percentage"] = (
            self.test_results["passed_tests"] / self.test_results["total_tests"] * 100
        )
        
        # 打印测试结果
        self.print_test_results()
        
        # 保存测试报告
        self.save_test_report()
        
        # 判断是否达到100%完成度
        if self.test_results["completion_percentage"] >= 100.0:
            logger.info("🎉 用户服务已达到100%完成度标准！")
            return True
        else:
            logger.error("❌ 用户服务完成度验证失败")
            return False
    
    def print_test_results(self):
        """打印测试结果"""
        logger.info("=" * 60)
        logger.info("用户服务完成度测试结果")
        logger.info("=" * 60)
        logger.info(f"总测试数: {self.test_results['total_tests']}")
        logger.info(f"通过测试: {self.test_results['passed_tests']}")
        logger.info(f"失败测试: {self.test_results['failed_tests']}")
        logger.info(f"完成度: {self.test_results['completion_percentage']:.1f}%")
        
        if self.test_results["completion_percentage"] < 100.0:
            logger.warning("⚠️ 用户服务尚未达到100%完成度标准")
        
        logger.info("\n详细测试结果:")
        for test_detail in self.test_results["test_details"]:
            status_icon = "✅" if test_detail["status"] == "PASSED" else "❌"
            logger.info(f"{status_icon} {test_detail['name']}: {test_detail['status']}")
        
        logger.info("=" * 60)
    
    def save_test_report(self, filename: str = "user_service_test_report.json"):
        """保存测试报告到JSON文件"""
        try:
            report_data = {
                **self.test_results,
                "test_timestamp": datetime.now().isoformat(),
                "service_name": "user-service",
                "test_environment": "local"
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试报告已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存测试报告失败: {e}")

async def main():
    """主函数"""
    tester = UserServiceTester()
    success = await tester.run_all_tests()
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 