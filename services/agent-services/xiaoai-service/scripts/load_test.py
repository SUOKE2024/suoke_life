#!/usr/bin/env python3
"""
小艾智能体负载测试脚本

用于测试系统在高并发情况下的性能表现
"""

import argparse
import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """测试结果"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    start_time: datetime
    end_time: datetime


class LoadTester:
    """负载测试器"""

    def __init__(
        self, base_url: str, concurrent_users: int = 10, total_requests: int = 1000
    ):
        self.base_url = base_url.rstrip("/")
        self.concurrent_users = concurrent_users
        self.total_requests = total_requests
        self.response_times: List[float] = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = None
        self.end_time = None

    async def make_request(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        method: str = "GET",
        data: Dict = None,
    ) -> float:
        """发送单个请求"""
        start_time = time.time()

        try:
            url = f"{self.base_url}{endpoint}"

            if method.upper() == "GET":
                async with session.get(url) as response:
                    await response.text()
                    if response.status < 400:
                        self.successful_requests += 1
                    else:
                        self.failed_requests += 1

            elif method.upper() == "POST":
                async with session.post(url, json=data) as response:
                    await response.text()
                    if response.status < 400:
                        self.successful_requests += 1
                    else:
                        self.failed_requests += 1

            response_time = time.time() - start_time
            self.response_times.append(response_time)
            return response_time

        except Exception as e:
            logger.error(f"请求失败: {e}")
            self.failed_requests += 1
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            return response_time

    async def user_simulation(self, session: aiohttp.ClientSession, user_id: int):
        """模拟单个用户的行为"""
        requests_per_user = self.total_requests // self.concurrent_users

        for i in range(requests_per_user):
            # 健康检查
            await self.make_request(session, "/health")

            # 模拟诊断请求
            diagnosis_data = {
                "session_id": f"test_session_{user_id}_{i}",
                "user_id": f"test_user_{user_id}",
                "diagnosis_types": ["looking", "listening", "inquiry"],
                "data": {
                    "symptoms": ["头痛", "失眠", "食欲不振"],
                    "duration": "3天",
                    "severity": "中等",
                },
            }
            await self.make_request(
                session, "/api/diagnosis/coordinate", "POST", diagnosis_data
            )

            # 模拟体质分析请求
            constitution_data = {
                "user_id": f"test_user_{user_id}",
                "questionnaire_data": {
                    "age": 30,
                    "gender": "male",
                    "symptoms": ["易疲劳", "怕冷", "消化不良"],
                },
            }
            await self.make_request(
                session, "/api/constitution/analyze", "POST", constitution_data
            )

            # 添加随机延迟模拟真实用户行为
            await asyncio.sleep(0.1)

    async def run_test(self) -> TestResult:
        """运行负载测试"""
        logger.info(
            f"开始负载测试: {self.concurrent_users}个并发用户, {self.total_requests}个总请求"
        )

        self.start_time = datetime.now()

        # 创建HTTP会话
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=self.concurrent_users * 2)

        async with aiohttp.ClientSession(
            timeout=timeout, connector=connector
        ) as session:
            # 创建并发任务
            tasks = [
                self.user_simulation(session, user_id)
                for user_id in range(self.concurrent_users)
            ]

            # 等待所有任务完成
            await asyncio.gather(*tasks)

        self.end_time = datetime.now()

        # 计算统计结果
        return self._calculate_results()

    def _calculate_results(self) -> TestResult:
        """计算测试结果"""
        if not self.response_times:
            raise ValueError("没有响应时间数据")

        sorted_times = sorted(self.response_times)
        total_time = (self.end_time - self.start_time).total_seconds()

        return TestResult(
            total_requests=len(self.response_times),
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            avg_response_time=sum(self.response_times) / len(self.response_times),
            min_response_time=min(self.response_times),
            max_response_time=max(self.response_times),
            p95_response_time=sorted_times[int(len(sorted_times) * 0.95)],
            p99_response_time=sorted_times[int(len(sorted_times) * 0.99)],
            requests_per_second=len(self.response_times) / total_time,
            error_rate=self.failed_requests / len(self.response_times) * 100,
            start_time=self.start_time,
            end_time=self.end_time,
        )


def print_results(result: TestResult):
    """打印测试结果"""
    print("\n" + "=" * 60)
    print("负载测试结果")
    print("=" * 60)
    print(f"测试时间: {result.start_time} - {result.end_time}")
    print(f"总请求数: {result.total_requests}")
    print(f"成功请求: {result.successful_requests}")
    print(f"失败请求: {result.failed_requests}")
    print(f"错误率: {result.error_rate:.2f}%")
    print(f"每秒请求数: {result.requests_per_second:.2f}")
    print("\n响应时间统计:")
    print(f"  平均响应时间: {result.avg_response_time*1000:.2f}ms")
    print(f"  最小响应时间: {result.min_response_time*1000:.2f}ms")
    print(f"  最大响应时间: {result.max_response_time*1000:.2f}ms")
    print(f"  95%响应时间: {result.p95_response_time*1000:.2f}ms")
    print(f"  99%响应时间: {result.p99_response_time*1000:.2f}ms")
    print("=" * 60)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="小艾智能体负载测试")
    parser.add_argument("--url", default="http://localhost:8000", help="服务URL")
    parser.add_argument("--users", type=int, default=10, help="并发用户数")
    parser.add_argument("--requests", type=int, default=1000, help="总请求数")
    parser.add_argument("--output", help="结果输出文件")

    args = parser.parse_args()

    # 创建负载测试器
    tester = LoadTester(
        base_url=args.url, concurrent_users=args.users, total_requests=args.requests
    )

    try:
        # 运行测试
        result = await tester.run_test()

        # 打印结果
        print_results(result)

        # 保存结果到文件
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "total_requests": result.total_requests,
                        "successful_requests": result.successful_requests,
                        "failed_requests": result.failed_requests,
                        "avg_response_time": result.avg_response_time,
                        "min_response_time": result.min_response_time,
                        "max_response_time": result.max_response_time,
                        "p95_response_time": result.p95_response_time,
                        "p99_response_time": result.p99_response_time,
                        "requests_per_second": result.requests_per_second,
                        "error_rate": result.error_rate,
                        "start_time": result.start_time.isoformat(),
                        "end_time": result.end_time.isoformat(),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            print(f"\n结果已保存到: {args.output}")

    except Exception as e:
        logger.error(f"负载测试失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
