#!/usr/bin/env python3
"""
索儿服务负载测试
"""
import argparse
import asyncio
import json
import os
import random
import sys
import time
import uuid
from datetime import datetime

import aiohttp
import matplotlib.pyplot as plt
import numpy as np
from tqdm.asyncio import tqdm_asyncio

# 确保能够导入应用代码
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


# 配置参数
DEFAULT_REST_URL = "http://localhost:8054"
DEFAULT_GRPC_URL = "localhost:50054"

class LoadTester:
    """负载测试器"""

    def __init__(self, rest_url=DEFAULT_REST_URL, grpc_url=DEFAULT_GRPC_URL):
        """初始化"""
        self.rest_url = rest_url
        self.grpc_url = grpc_url
        self.results = {
            "health_check": [],
            "health_plan_create": [],
            "emotional_analysis": []
        }
        self.errors = {
            "health_check": [],
            "health_plan_create": [],
            "emotional_analysis": []
        }

    async def test_health_check(self, num_requests, concurrent_limit):
        """测试健康检查接口性能"""
        print(f"\n开始健康检查接口负载测试: {num_requests}个请求, 并发限制 {concurrent_limit}")

        async def health_check_request():
            """健康检查请求"""
            start_time = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.rest_url}/health") as response:
                        await response.text()
                duration = time.time() - start_time
                self.results["health_check"].append(duration)
                return True
            except Exception as e:
                self.errors["health_check"].append(str(e))
                return False

        # 使用信号量限制并发
        semaphore = asyncio.Semaphore(concurrent_limit)

        async def bounded_health_check():
            """使用信号量限制的健康检查"""
            async with semaphore:
                return await health_check_request()

        # 创建并执行请求
        tasks = [bounded_health_check() for _ in range(num_requests)]
        results = await tqdm_asyncio.gather(*tasks)

        # 统计成功率
        success_count = results.count(True)
        success_rate = (success_count / num_requests) * 100

        print(f"健康检查接口测试完成: 成功率 {success_rate:.2f}%")
        self._print_statistics("health_check")

    async def test_health_plan_create(self, num_requests, concurrent_limit):
        """测试健康计划创建接口性能"""
        print(f"\n开始健康计划创建接口负载测试: {num_requests}个请求, 并发限制 {concurrent_limit}")

        async def health_plan_request():
            """健康计划创建请求"""
            # 生成随机用户ID
            user_id = f"test_user_{uuid.uuid4().hex[:8]}"

            # 随机选择体质类型
            constitution_types = ["阳虚质", "阴虚质", "气虚质", "痰湿质", "湿热质", "血瘀质", "气郁质", "特禀质", "平和质"]
            constitution_type = random.choice(constitution_types)

            # 随机选择健康目标
            all_goals = ["改善睡眠", "增强体质", "减轻压力", "提高免疫力", "改善消化", "缓解疲劳", "稳定情绪", "增强心肺功能"]
            health_goals = random.sample(all_goals, k=random.randint(1, 3))

            # 生成随机健康数据
            health_data = {
                "height": random.randint(155, 190),
                "weight": random.randint(45, 90),
                "blood_pressure": f"{random.randint(100, 140)}/{random.randint(60, 90)}",
                "heart_rate": random.randint(60, 100),
                "sleep_duration": round(random.uniform(5.0, 9.0), 1),
                "activity_level": random.choice(["low", "moderate", "high"])
            }

            # 构建请求数据
            request_data = {
                "user_id": user_id,
                "constitution_type": constitution_type,
                "health_goals": health_goals,
                "health_data": health_data
            }

            # 发送请求并记录时间
            start_time = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.rest_url}/health-plans/",
                        json=request_data
                    ) as response:
                        await response.text()
                duration = time.time() - start_time
                self.results["health_plan_create"].append(duration)
                return True
            except Exception as e:
                self.errors["health_plan_create"].append(str(e))
                return False

        # 使用信号量限制并发
        semaphore = asyncio.Semaphore(concurrent_limit)

        async def bounded_health_plan_request():
            """使用信号量限制的健康计划创建请求"""
            async with semaphore:
                return await health_plan_request()

        # 创建并执行请求
        tasks = [bounded_health_plan_request() for _ in range(num_requests)]
        results = await tqdm_asyncio.gather(*tasks)

        # 统计成功率
        success_count = results.count(True)
        success_rate = (success_count / num_requests) * 100

        print(f"健康计划创建接口测试完成: 成功率 {success_rate:.2f}%")
        self._print_statistics("health_plan_create")

    async def test_emotional_analysis(self, num_requests, concurrent_limit):
        """测试情绪分析接口性能"""
        print(f"\n开始情绪分析接口负载测试: {num_requests}个请求, 并发限制 {concurrent_limit}")

        # 情绪文本样本
        emotion_texts = [
            "我今天感到非常生气，因为工作中遇到了很多问题，心情很糟糕。",
            "这几天一直很开心，和家人一起度过了愉快的周末。",
            "我有点担心最近的健康状况，可能需要去医院检查一下。",
            "最近工作很忙，但是心情还算平静，没有太大的波动。",
            "我非常难过，感觉自己的努力都没有得到回报。",
            "今天天气不错，心情舒畅，感觉精力充沛。",
            "我很焦虑，总是担心未来会发生什么。",
            "刚收到一个好消息，感到非常兴奋！",
            "这段时间经常感到疲倦和无力，不知道是怎么回事。",
            "刚刚受到了表扬，感到很自豪和满足。"
        ]

        async def emotional_analysis_request():
            """情绪分析请求"""
            # 生成随机用户ID
            user_id = f"test_user_{uuid.uuid4().hex[:8]}"

            # 随机选择情绪文本
            text = random.choice(emotion_texts)

            # 构建请求数据
            request_data = {
                "user_id": user_id,
                "inputs": [
                    {
                        "input_type": "text",
                        "data": text,
                        "metadata": {
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                ]
            }

            # 发送请求并记录时间
            start_time = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.rest_url}/emotion/analyze",
                        json=request_data
                    ) as response:
                        await response.text()
                duration = time.time() - start_time
                self.results["emotional_analysis"].append(duration)
                return True
            except Exception as e:
                self.errors["emotional_analysis"].append(str(e))
                return False

        # 使用信号量限制并发
        semaphore = asyncio.Semaphore(concurrent_limit)

        async def bounded_emotional_analysis_request():
            """使用信号量限制的情绪分析请求"""
            async with semaphore:
                return await emotional_analysis_request()

        # 创建并执行请求
        tasks = [bounded_emotional_analysis_request() for _ in range(num_requests)]
        results = await tqdm_asyncio.gather(*tasks)

        # 统计成功率
        success_count = results.count(True)
        success_rate = (success_count / num_requests) * 100

        print(f"情绪分析接口测试完成: 成功率 {success_rate:.2f}%")
        self._print_statistics("emotional_analysis")

    def _print_statistics(self, test_name):
        """打印统计信息"""
        durations = self.results[test_name]
        if not durations:
            print(f"没有成功的{test_name}请求")
            return

        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        p95_duration = sorted(durations)[int(len(durations) * 0.95)]
        p99_duration = sorted(durations)[int(len(durations) * 0.99)]

        print(f"  平均响应时间: {avg_duration:.4f}秒")
        print(f"  最小响应时间: {min_duration:.4f}秒")
        print(f"  最大响应时间: {max_duration:.4f}秒")
        print(f"  95%响应时间: {p95_duration:.4f}秒")
        print(f"  99%响应时间: {p99_duration:.4f}秒")
        print(f"  错误数量: {len(self.errors[test_name])}")

    def generate_report(self, output_dir="test/performance/reports"):
        """生成测试报告"""
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 报告时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 报告文件路径
        report_file = os.path.join(output_dir, f"load_test_report_{timestamp}.json")
        chart_file = os.path.join(output_dir, f"load_test_chart_{timestamp}.png")

        # 生成JSON报告
        report_data = {
            "timestamp": timestamp,
            "results": {
                test_name: {
                    "count": len(durations),
                    "avg": sum(durations) / len(durations) if durations else 0,
                    "min": min(durations) if durations else 0,
                    "max": max(durations) if durations else 0,
                    "p95": sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
                    "p99": sorted(durations)[int(len(durations) * 0.99)] if durations else 0,
                    "errors": len(self.errors[test_name])
                }
                for test_name, durations in self.results.items() if durations
            }
        }

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        # 生成图表
        self._generate_chart(chart_file)

        print(f"\n测试报告已生成: {report_file}")
        print(f"测试图表已生成: {chart_file}")

    def _generate_chart(self, chart_file):
        """生成测试图表"""
        plt.figure(figsize=(12, 8))

        # 绘制响应时间分布直方图
        for i, (test_name, durations) in enumerate(self.results.items(), 1):
            if not durations:
                continue

            plt.subplot(2, 2, i)
            plt.hist(durations, bins=30, alpha=0.7)
            plt.title(f"{test_name} 响应时间分布")
            plt.xlabel("响应时间 (秒)")
            plt.ylabel("请求数量")
            plt.grid(True, alpha=0.3)

        # 绘制比较图
        plt.subplot(2, 2, 4)
        labels = []
        avg_times = []
        p95_times = []
        p99_times = []

        for test_name, durations in self.results.items():
            if not durations:
                continue

            labels.append(test_name)
            avg_times.append(sum(durations) / len(durations))
            p95_times.append(sorted(durations)[int(len(durations) * 0.95)])
            p99_times.append(sorted(durations)[int(len(durations) * 0.99)])

        x = np.arange(len(labels))
        width = 0.25

        plt.bar(x - width, avg_times, width, label='平均')
        plt.bar(x, p95_times, width, label='P95')
        plt.bar(x + width, p99_times, width, label='P99')

        plt.title("响应时间比较")
        plt.xlabel("接口")
        plt.ylabel("响应时间 (秒)")
        plt.xticks(x, labels)
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(chart_file)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="索儿服务负载测试")
    parser.add_argument("--rest-url", default=DEFAULT_REST_URL, help="REST API URL")
    parser.add_argument("--grpc-url", default=DEFAULT_GRPC_URL, help="gRPC服务URL")
    parser.add_argument("--requests", type=int, default=100, help="每个接口的请求数")
    parser.add_argument("--concurrency", type=int, default=10, help="并发请求数量")
    args = parser.parse_args()

    # 创建负载测试器
    tester = LoadTester(args.rest_url, args.grpc_url)

    # 执行测试
    await tester.test_health_check(args.requests, args.concurrency)
    await tester.test_health_plan_create(args.requests, args.concurrency)
    await tester.test_emotional_analysis(args.requests, args.concurrency)

    # 生成报告
    tester.generate_report()


if __name__ == "__main__":
    asyncio.run(main())
