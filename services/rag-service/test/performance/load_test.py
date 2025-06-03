#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG服务负载测试脚本

使用方法:
    python load_test.py --url http://localhost:8000 --users 10 --time 30
"""

import argparse
import asyncio
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import statistics

import aiohttp
from loguru import logger

@dataclass
class TestResult:
    """测试结果数据类"""
    endpoint: str
    status_code: int
    response_time: float
    success: bool
    error: Optional[str] = None

class LoadTester:
    """负载测试器类"""
    
    def __init__(
        self,
        base_url: str,
        num_users: int = 10,
        test_duration: int = 60,
        ramp_up: int = 5
    ):
        """
        初始化负载测试器
        
        Args:
            base_url: 基础URL
            num_users: 并发用户数
            test_duration: 测试持续时间（秒）
            ramp_up: 用户增长时间（秒）
        """
        self.base_url = base_url
        self.num_users = num_users
        self.test_duration = test_duration
        self.ramp_up = ramp_up
        
        self.results: List[TestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 测试数据
        self.test_queries = [
            "中医如何看待感冒?",
            "高血压的中医治疗方法有哪些?",
            "失眠应该如何调理?",
            "四诊合参的具体含义是什么?",
            "肝火旺有哪些表现?",
            "针灸如何治疗颈椎病?",
            "中医脉诊的基本方法是什么?",
            "气虚和血虚有什么区别?",
            "阴虚和阳虚的区别是什么?",
            "五行学说与中医的关系?",
            "中医体质分为哪几种?",
            "湿热体质应该如何调理?",
            "中药有哪些常见的配伍禁忌?",
            "太阳病的症状有哪些特点?",
            "立春养生应该注意什么?"
        ]
    
    async def setup(self):
        """设置会话"""
        self.session = aiohttp.ClientSession()
    
    async def teardown(self):
        """清理会话"""
        if self.session:
            await self.session.close()
    
    async def send_retrieve_request(self) -> TestResult:
        """发送检索请求"""
        query = random.choice(self.test_queries)
        url = f"{self.base_url}/api/v1/retrieve"
        
        payload = {
            "query": query,
            "top_k": random.choice([3, 5, 8]),
            "filter": {}
        }
        
        start_time = time.time()
        
        try:
            async with self.session.post(url, json=payload) as response:
                response_time = time.time() - start_time
                status_code = response.status
                success = 200 <= status_code < 300
                
                if success:
                    return TestResult(
                        endpoint="retrieve",
                        status_code=status_code,
                        response_time=response_time,
                        success=True
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        endpoint="retrieve",
                        status_code=status_code,
                        response_time=response_time,
                        success=False,
                        error=error_text[:100]
                    )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint="retrieve",
                status_code=500,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    async def send_query_request(self) -> TestResult:
        """发送查询请求"""
        query = random.choice(self.test_queries)
        url = f"{self.base_url}/api/v1/query"
        
        payload = {
            "query": query,
            "top_k": random.choice([3, 5, 8]),
            "filter": {}
        }
        
        start_time = time.time()
        
        try:
            async with self.session.post(url, json=payload) as response:
                response_time = time.time() - start_time
                status_code = response.status
                success = 200 <= status_code < 300
                
                if success:
                    return TestResult(
                        endpoint="query",
                        status_code=status_code,
                        response_time=response_time,
                        success=True
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        endpoint="query",
                        status_code=status_code,
                        response_time=response_time,
                        success=False,
                        error=error_text[:100]
                    )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint="query",
                status_code=500,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    async def send_health_request(self) -> TestResult:
        """发送健康检查请求"""
        url = f"{self.base_url}/health"
        
        start_time = time.time()
        
        try:
            async with self.session.get(url) as response:
                response_time = time.time() - start_time
                status_code = response.status
                success = 200 <= status_code < 300
                
                if success:
                    return TestResult(
                        endpoint="health",
                        status_code=status_code,
                        response_time=response_time,
                        success=True
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        endpoint="health",
                        status_code=status_code,
                        response_time=response_time,
                        success=False,
                        error=error_text[:100]
                    )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint="health",
                status_code=500,
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    async def user_behavior(self, user_id: int):
        """
        模拟用户行为
        
        Args:
            user_id: 用户ID
        """
        logger.info(f"User {user_id} started")
        
        start_time = time.time()
        end_time = start_time + self.test_duration
        
        while time.time() < end_time:
            # 随机选择一个请求类型
            request_type = random.choices(
                ["retrieve", "query", "health"],
                weights=[0.4, 0.4, 0.2],
                k=1
            )[0]
            
            if request_type == "retrieve":
                result = await self.send_retrieve_request()
            elif request_type == "query":
                result = await self.send_query_request()
            else:
                result = await self.send_health_request()
            
            self.results.append(result)
            
            # 用户思考时间（0.5-3秒）
            think_time = random.uniform(0.5, 3.0)
            await asyncio.sleep(think_time)
        
        logger.info(f"User {user_id} finished")
    
    async def run(self):
        """执行负载测试"""
        await self.setup()
        
        logger.info(f"Starting load test with {self.num_users} users for {self.test_duration} seconds")
        logger.info(f"Ramp-up time: {self.ramp_up} seconds")
        
        tasks = []
        
        # 计算用户启动间隔
        if self.num_users > 1:
            delay_between_users = self.ramp_up / (self.num_users - 1)
        else:
            delay_between_users = 0
        
        # 创建并启动用户任务
        for i in range(self.num_users):
            user_task = asyncio.create_task(self.user_behavior(i + 1))
            tasks.append(user_task)
            
            if i < self.num_users - 1:
                await asyncio.sleep(delay_between_users)
        
        # 等待所有任务完成
        await asyncio.gather(*tasks)
        
        await self.teardown()
        
        logger.info("Load test completed")
    
    def generate_report(self):
        """生成测试报告"""
        if not self.results:
            logger.error("No test results to generate report from")
            return
        
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        success_rate = successful_requests / total_requests * 100
        
        # 按端点分组结果
        endpoint_results = {}
        for result in self.results:
            if result.endpoint not in endpoint_results:
                endpoint_results[result.endpoint] = []
            endpoint_results[result.endpoint].append(result)
        
        logger.info(f"Total requests: {total_requests}")
        logger.info(f"Successful requests: {successful_requests} ({success_rate:.2f}%)")
        
        # 计算每个端点的统计信息
        for endpoint, results in endpoint_results.items():
            response_times = [r.response_time for r in results]
            success_count = sum(1 for r in results if r.success)
            success_rate = success_count / len(results) * 100
            
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            p90_time = np.percentile(response_times, 90)
            p95_time = np.percentile(response_times, 95)
            p99_time = np.percentile(response_times, 99)
            
            logger.info(f"\nEndpoint: {endpoint}")
            logger.info(f"  Requests: {len(results)}")
            logger.info(f"  Success rate: {success_rate:.2f}%")
            logger.info(f"  Min response time: {min_time:.3f}s")
            logger.info(f"  Avg response time: {avg_time:.3f}s")
            logger.info(f"  Max response time: {max_time:.3f}s")
            logger.info(f"  90th percentile: {p90_time:.3f}s")
            logger.info(f"  95th percentile: {p95_time:.3f}s")
            logger.info(f"  99th percentile: {p99_time:.3f}s")
        
        # 创建图表
        self._create_charts(endpoint_results)
    
    def _create_charts(self, endpoint_results: Dict[str, List[TestResult]]):
        """
        创建图表
        
        Args:
            endpoint_results: 按端点分组的测试结果
        """
        # 创建响应时间直方图
        plt.figure(figsize=(12, 8))
        
        for i, (endpoint, results) in enumerate(endpoint_results.items()):
            response_times = [r.response_time for r in results]
            
            plt.subplot(len(endpoint_results), 2, i*2+1)
            plt.hist(response_times, bins=20, alpha=0.7, color=f"C{i}")
            plt.title(f"{endpoint} Response Time Distribution")
            plt.xlabel("Response Time (s)")
            plt.ylabel("Count")
            
            # 按时间顺序的散点图
            plt.subplot(len(endpoint_results), 2, i*2+2)
            plt.scatter(range(len(results)), response_times, alpha=0.5, s=10, color=f"C{i}")
            plt.title(f"{endpoint} Response Time Over Time")
            plt.xlabel("Request #")
            plt.ylabel("Response Time (s)")
        
        plt.tight_layout()
        plt.savefig("load_test_results.png")
        logger.info("Charts saved to load_test_results.png")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="RAG服务负载测试")
    parser.add_argument("--url", type=str, default="http://localhost:8000", help="服务基础URL")
    parser.add_argument("--users", type=int, default=10, help="并发用户数")
    parser.add_argument("--time", type=int, default=60, help="测试持续时间（秒）")
    parser.add_argument("--ramp-up", type=int, default=5, help="用户递增时间（秒）")
    
    return parser.parse_args()

async def main():
    """主函数"""
    args = parse_args()
    
    tester = LoadTester(
        base_url=args.url,
        num_users=args.users,
        test_duration=args.time,
        ramp_up=args.ramp_up
    )
    
    await tester.run()
    tester.generate_report()

if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(
        "load_test.log",
        rotation="10 MB",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(
        lambda msg: print(msg),
        level="INFO",
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>"
    )
    
    # 执行测试
    asyncio.run(main()) 