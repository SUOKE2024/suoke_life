#!/usr/bin/env python3
"""
负载测试运行器
使用Locust进行Auth-Service和User-Service的负载测试
"""

import asyncio
import aiohttp
import json
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import argparse


@dataclass
class LoadTestConfig:
    """负载测试配置"""
    auth_service_url: str = "http://localhost:8001"
    user_service_url: str = "http://localhost:8002"
    concurrent_users: int = 50
    test_duration: int = 60  # 秒
    ramp_up_time: int = 10   # 秒
    target_rps: int = 100    # 目标每秒请求数


class LoadTestMetrics:
    """负载测试指标收集器"""
    
    def __init__(self):
        self.requests = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def add_request(self, endpoint: str, response_time: float, status_code: int, success: bool):
        """添加请求记录"""
        self.requests.append({
            "timestamp": time.time(),
            "endpoint": endpoint,
            "response_time": response_time,
            "status_code": status_code,
            "success": success
        })
        
        if not success:
            self.errors.append({
                "timestamp": time.time(),
                "endpoint": endpoint,
                "status_code": status_code,
                "response_time": response_time
            })
    
    def get_summary(self) -> Dict:
        """获取测试总结"""
        if not self.requests:
            return {}
        
        total_requests = len(self.requests)
        successful_requests = len([r for r in self.requests if r["success"]])
        failed_requests = total_requests - successful_requests
        
        response_times = [r["response_time"] for r in self.requests if r["success"]]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max_response_time
            p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max_response_time
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0
        
        test_duration = (self.end_time - self.start_time) if self.start_time and self.end_time else 0
        rps = total_requests / test_duration if test_duration > 0 else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "p95_response_time": p95_response_time,
            "p99_response_time": p99_response_time,
            "requests_per_second": rps,
            "test_duration": test_duration,
            "error_rate": failed_requests / total_requests if total_requests > 0 else 0
        }


class AuthServiceLoadTester:
    """Auth-Service负载测试器"""
    
    def __init__(self, base_url: str, metrics: LoadTestMetrics):
        self.base_url = base_url
        self.metrics = metrics
        self.session = None
    
    async def setup(self):
        """设置测试环境"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
    
    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
    
    async def test_user_registration(self, user_id: int) -> bool:
        """测试用户注册"""
        start_time = time.time()
        
        try:
            user_data = {
                "username": f"loadtest_user_{user_id}_{int(time.time())}",
                "email": f"loadtest_{user_id}_{int(time.time())}@suoke.life",
                "password": "LoadTest123!",
                "confirm_password": "LoadTest123!",
                "full_name": f"Load Test User {user_id}"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/users/",
                json=user_data
            ) as response:
                response_time = time.time() - start_time
                success = response.status in [200, 201]
                
                self.metrics.add_request(
                    "POST /api/v1/users/",
                    response_time,
                    response.status,
                    success
                )
                
                return success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.add_request(
                "POST /api/v1/users/",
                response_time,
                0,
                False
            )
            return False
    
    async def test_user_login(self, username: str, password: str) -> Optional[str]:
        """测试用户登录"""
        start_time = time.time()
        
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                self.metrics.add_request(
                    "POST /api/v1/auth/login",
                    response_time,
                    response.status,
                    success
                )
                
                if success:
                    data = await response.json()
                    return data.get("access_token")
                
                return None
                
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.add_request(
                "POST /api/v1/auth/login",
                response_time,
                0,
                False
            )
            return None
    
    async def test_token_validation(self, token: str) -> bool:
        """测试令牌验证"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=headers
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                self.metrics.add_request(
                    "GET /api/v1/auth/me",
                    response_time,
                    response.status,
                    success
                )
                
                return success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.add_request(
                "GET /api/v1/auth/me",
                response_time,
                0,
                False
            )
            return False


class UserServiceLoadTester:
    """User-Service负载测试器"""
    
    def __init__(self, base_url: str, metrics: LoadTestMetrics):
        self.base_url = base_url
        self.metrics = metrics
        self.session = None
    
    async def setup(self):
        """设置测试环境"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
    
    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
    
    async def test_user_creation(self, user_id: int) -> Optional[str]:
        """测试用户创建"""
        start_time = time.time()
        
        try:
            user_data = {
                "username": f"userservice_test_{user_id}_{int(time.time())}",
                "email": f"usertest_{user_id}_{int(time.time())}@suoke.life",
                "full_name": f"User Service Test {user_id}",
                "phone": f"+861380013{user_id:04d}",
                "date_of_birth": "1990-01-01"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/users",
                json=user_data
            ) as response:
                response_time = time.time() - start_time
                success = response.status in [200, 201]
                
                self.metrics.add_request(
                    "POST /api/v1/users",
                    response_time,
                    response.status,
                    success
                )
                
                if success:
                    data = await response.json()
                    return data.get("id")
                
                return None
                
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.add_request(
                "POST /api/v1/users",
                response_time,
                0,
                False
            )
            return None
    
    async def test_user_retrieval(self, user_id: str) -> bool:
        """测试用户查询"""
        start_time = time.time()
        
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/users/{user_id}"
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                self.metrics.add_request(
                    "GET /api/v1/users/{id}",
                    response_time,
                    response.status,
                    success
                )
                
                return success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.add_request(
                "GET /api/v1/users/{id}",
                response_time,
                0,
                False
            )
            return False
    
    async def test_user_update(self, user_id: str) -> bool:
        """测试用户更新"""
        start_time = time.time()
        
        try:
            update_data = {
                "full_name": f"Updated User {int(time.time())}",
                "phone": f"+861380013{int(time.time()) % 10000:04d}"
            }
            
            async with self.session.put(
                f"{self.base_url}/api/v1/users/{user_id}",
                json=update_data
            ) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                self.metrics.add_request(
                    "PUT /api/v1/users/{id}",
                    response_time,
                    response.status,
                    success
                )
                
                return success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.add_request(
                "PUT /api/v1/users/{id}",
                response_time,
                0,
                False
            )
            return False


class LoadTestRunner:
    """负载测试运行器"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.auth_metrics = LoadTestMetrics()
        self.user_metrics = LoadTestMetrics()
    
    async def run_auth_service_load_test(self):
        """运行Auth-Service负载测试"""
        print(f"🔐 开始Auth-Service负载测试 ({self.config.concurrent_users} 并发用户)")
        
        tester = AuthServiceLoadTester(self.config.auth_service_url, self.auth_metrics)
        await tester.setup()
        
        try:
            self.auth_metrics.start_time = time.time()
            
            # 创建并发任务
            tasks = []
            for i in range(self.config.concurrent_users):
                task = asyncio.create_task(self._auth_user_workflow(tester, i))
                tasks.append(task)
                
                # 渐进式增加负载
                if i < self.config.concurrent_users - 1:
                    await asyncio.sleep(self.config.ramp_up_time / self.config.concurrent_users)
            
            # 等待所有任务完成
            await asyncio.gather(*tasks, return_exceptions=True)
            
            self.auth_metrics.end_time = time.time()
            
        finally:
            await tester.cleanup()
    
    async def _auth_user_workflow(self, tester: AuthServiceLoadTester, user_id: int):
        """Auth-Service用户工作流"""
        end_time = time.time() + self.config.test_duration
        
        while time.time() < end_time:
            # 1. 用户注册
            registration_success = await tester.test_user_registration(user_id)
            
            if registration_success:
                # 2. 用户登录
                username = f"loadtest_user_{user_id}_{int(time.time())}"
                token = await tester.test_user_login(username, "LoadTest123!")
                
                if token:
                    # 3. 令牌验证
                    await tester.test_token_validation(token)
            
            # 控制请求频率
            await asyncio.sleep(1.0 / (self.config.target_rps / self.config.concurrent_users))
    
    async def run_user_service_load_test(self):
        """运行User-Service负载测试"""
        print(f"👤 开始User-Service负载测试 ({self.config.concurrent_users} 并发用户)")
        
        tester = UserServiceLoadTester(self.config.user_service_url, self.user_metrics)
        await tester.setup()
        
        try:
            self.user_metrics.start_time = time.time()
            
            # 创建并发任务
            tasks = []
            for i in range(self.config.concurrent_users):
                task = asyncio.create_task(self._user_service_workflow(tester, i))
                tasks.append(task)
                
                # 渐进式增加负载
                if i < self.config.concurrent_users - 1:
                    await asyncio.sleep(self.config.ramp_up_time / self.config.concurrent_users)
            
            # 等待所有任务完成
            await asyncio.gather(*tasks, return_exceptions=True)
            
            self.user_metrics.end_time = time.time()
            
        finally:
            await tester.cleanup()
    
    async def _user_service_workflow(self, tester: UserServiceLoadTester, user_id: int):
        """User-Service用户工作流"""
        end_time = time.time() + self.config.test_duration
        created_users = []
        
        while time.time() < end_time:
            # 1. 创建用户
            new_user_id = await tester.test_user_creation(user_id)
            
            if new_user_id:
                created_users.append(new_user_id)
                
                # 2. 查询用户
                await tester.test_user_retrieval(new_user_id)
                
                # 3. 更新用户
                await tester.test_user_update(new_user_id)
            
            # 对已创建的用户进行随机操作
            if created_users:
                import random
                random_user = random.choice(created_users)
                await tester.test_user_retrieval(random_user)
            
            # 控制请求频率
            await asyncio.sleep(1.0 / (self.config.target_rps / self.config.concurrent_users))
    
    async def run_full_load_test(self):
        """运行完整负载测试"""
        print("🚀 开始完整负载测试...")
        
        # 并行运行两个服务的负载测试
        auth_task = asyncio.create_task(self.run_auth_service_load_test())
        user_task = asyncio.create_task(self.run_user_service_load_test())
        
        await asyncio.gather(auth_task, user_task, return_exceptions=True)
        
        # 生成测试报告
        self.generate_load_test_report()
    
    def generate_load_test_report(self):
        """生成负载测试报告"""
        auth_summary = self.auth_metrics.get_summary()
        user_summary = self.user_metrics.get_summary()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "concurrent_users": self.config.concurrent_users,
                "test_duration": self.config.test_duration,
                "target_rps": self.config.target_rps
            },
            "auth_service": auth_summary,
            "user_service": user_summary
        }
        
        # 保存JSON报告
        with open("load_test_metrics.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # 打印摘要
        print("\n📊 负载测试结果摘要:")
        print(f"Auth-Service: {auth_summary.get('requests_per_second', 0):.1f} RPS, "
              f"成功率: {auth_summary.get('success_rate', 0)*100:.1f}%, "
              f"平均响应时间: {auth_summary.get('avg_response_time', 0)*1000:.1f}ms")
        print(f"User-Service: {user_summary.get('requests_per_second', 0):.1f} RPS, "
              f"成功率: {user_summary.get('success_rate', 0)*100:.1f}%, "
              f"平均响应时间: {user_summary.get('avg_response_time', 0)*1000:.1f}ms")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Auth & User Service 负载测试")
    parser.add_argument("--concurrent-users", type=int, default=50, help="并发用户数")
    parser.add_argument("--test-duration", type=int, default=60, help="测试持续时间(秒)")
    parser.add_argument("--target-rps", type=int, default=100, help="目标每秒请求数")
    parser.add_argument("--auth-url", default="http://localhost:8001", help="Auth-Service URL")
    parser.add_argument("--user-url", default="http://localhost:8002", help="User-Service URL")
    
    args = parser.parse_args()
    
    config = LoadTestConfig(
        auth_service_url=args.auth_url,
        user_service_url=args.user_url,
        concurrent_users=args.concurrent_users,
        test_duration=args.test_duration,
        target_rps=args.target_rps
    )
    
    runner = LoadTestRunner(config)
    await runner.run_full_load_test()


if __name__ == "__main__":
    asyncio.run(main()) 