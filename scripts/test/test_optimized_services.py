#!/usr/bin/env python3
"""
索克生活 - 优化服务测试脚本
测试所有优化的智能体服务功能
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List
from datetime import datetime


class OptimizedServiceTester:
    """优化服务测试器"""

    def __init__(self):
        self.base_urls = {
            "api_gateway": "http://localhost:8000",
            "xiaoai": "http://localhost:8001",
            "xiaoke": "http://localhost:8002",
            "laoke": "http://localhost:8003",
            "soer": "http://localhost:8004"
        }
        self.test_results = []

    async def test_service_health(self, service_name: str, url: str) -> Dict[str, Any]:
        """测试服务健康状态"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/health", timeout=10) as response:
                    if response.status == 200:
                        return {
                            "service": service_name,
                            "status": "healthy",
                            "response_time": response.headers.get("X-Response-Time", "N/A"),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "service": service_name,
                            "status": "unhealthy",
                            "status_code": response.status,
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def test_xiaoai_inference(self) -> Dict[str, Any]:
        """测试小艾AI推理功能"""
        test_data = {
            "request_id": "test_xiaoai_001",
            "user_id": "test_user",
            "query": "请分析这个健康数据",
            "context": {
                "health_data": [120, 80, 72, 36.5],
                "symptoms": ["轻微头痛", "疲劳"]
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    f"{self.base_urls['xiaoai']}/inference",
                    json=test_data,
                    timeout=30
                ) as response:
                    end_time = time.time()

                    if response.status == 200:
                        result = await response.json()
                        return {
                            "test": "xiaoai_inference",
                            "status": "success",
                            "response_time": f"{end_time - start_time:.2f}s",
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "test": "xiaoai_inference",
                            "status": "failed",
                            "status_code": response.status,
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            return {
                "test": "xiaoai_inference",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def test_xiaoke_monitoring(self) -> Dict[str, Any]:
        """测试小克健康监测功能"""
        test_data = {
            "request_id": "test_xiaoke_001",
            "user_id": "test_user",
            "vital_signs": {
                "blood_pressure": {"systolic": 120, "diastolic": 80},
                "heart_rate": 72,
                "temperature": 36.5
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    f"{self.base_urls['xiaoke']}/monitor",
                    json=test_data,
                    timeout=30
                ) as response:
                    end_time = time.time()

                    if response.status == 200:
                        result = await response.json()
                        return {
                            "test": "xiaoke_monitoring",
                            "status": "success",
                            "response_time": f"{end_time - start_time:.2f}s",
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "test": "xiaoke_monitoring",
                            "status": "failed",
                            "status_code": response.status,
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            return {
                "test": "xiaoke_monitoring",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def test_laoke_syndrome_analysis(self) -> Dict[str, Any]:
        """测试老克中医辨证功能"""
        test_data = {
            "request_id": "test_laoke_001",
            "user_id": "test_user",
            "symptoms": ["疲劳", "食欲不振", "腹胀"],
            "pulse": "沉脉",
            "tongue": "淡舌"
        }

        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    f"{self.base_urls['laoke']}/syndrome_analysis",
                    json=test_data,
                    timeout=30
                ) as response:
                    end_time = time.time()

                    if response.status == 200:
                        result = await response.json()
                        return {
                            "test": "laoke_syndrome_analysis",
                            "status": "success",
                            "response_time": f"{end_time - start_time:.2f}s",
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "test": "laoke_syndrome_analysis",
                            "status": "failed",
                            "status_code": response.status,
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            return {
                "test": "laoke_syndrome_analysis",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def test_soer_lifestyle_plan(self) -> Dict[str, Any]:
        """测试索儿生活方式规划功能"""
        test_data = {
            "request_id": "test_soer_001",
            "user_id": "test_user",
            "user_profile": {
                "age": 30,
                "gender": "female",
                "occupation": "office_worker"
            },
            "goals": ["减重", "改善睡眠", "增强体质"],
            "preferences": {
                "exercise_type": "yoga",
                "diet_style": "balanced"
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.post(
                    f"{self.base_urls['soer']}/lifestyle_plan",
                    json=test_data,
                    timeout=30
                ) as response:
                    end_time = time.time()

                    if response.status == 200:
                        result = await response.json()
                        return {
                            "test": "soer_lifestyle_plan",
                            "status": "success",
                            "response_time": f"{end_time - start_time:.2f}s",
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        return {
                            "test": "soer_lifestyle_plan",
                            "status": "failed",
                            "status_code": response.status,
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            return {
                "test": "soer_lifestyle_plan",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def test_performance_benchmark(self) -> Dict[str, Any]:
        """性能基准测试"""
        print("开始性能基准测试...")

        # 并发请求测试
        concurrent_requests = 10
        tasks = []

        # 创建并发任务
        for i in range(concurrent_requests):
            tasks.extend([
                self.test_xiaoai_inference(),
                self.test_xiaoke_monitoring(),
                self.test_laoke_syndrome_analysis(),
                self.test_soer_lifestyle_plan()
            ])

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # 统计结果
        successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        failed_requests = len(results) - successful_requests
        total_time = end_time - start_time

        return {
            "test": "performance_benchmark",
            "total_requests": len(results),
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": f"{(successful_requests / len(results)) * 100:.2f}%",
            "total_time": f"{total_time:.2f}s",
            "requests_per_second": f"{len(results) / total_time:.2f}",
            "average_response_time": f"{total_time / len(results):.2f}s",
            "timestamp": datetime.now().isoformat()
        }

    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("开始运行索克生活优化服务测试...")

        # 健康检查测试
        print("\n1. 服务健康检查...")
        health_tests = []
        for service_name, url in self.base_urls.items():
            health_tests.append(self.test_service_health(service_name, url))

        health_results = await asyncio.gather(*health_tests)

        # 功能测试
        print("\n2. 功能测试...")
        function_tests = [
            self.test_xiaoai_inference(),
            self.test_xiaoke_monitoring(),
            self.test_laoke_syndrome_analysis(),
            self.test_soer_lifestyle_plan()
        ]

        function_results = await asyncio.gather(*function_tests, return_exceptions=True)

        # 性能测试
        print("\n3. 性能基准测试...")
        performance_result = await self.test_performance_benchmark()

        # 汇总结果
        test_summary = {
            "test_suite": "suoke_life_optimized_services",
            "test_time": datetime.now().isoformat(),
            "health_check": {
                "total_services": len(health_results),
                "healthy_services": sum(1 for r in health_results if r.get("status") == "healthy"),
                "results": health_results
            },
            "function_tests": {
                "total_tests": len(function_tests),
                "successful_tests": sum(1 for r in function_results if isinstance(r, dict) and r.get("status") == "success"),
                "results": function_results
            },
            "performance_test": performance_result
        }

        return test_summary

    def print_test_results(self, results: Dict[str, Any]):
        """打印测试结果"""
        print("\n" + "="*60)
        print("索克生活优化服务测试报告")
        print("="*60)

        # 健康检查结果
        health_check = results["health_check"]
        print(f"\n健康检查: {health_check['healthy_services']}/{health_check['total_services']} 服务正常")

        for result in health_check["results"]:
            status_icon = "✅" if result["status"] == "healthy" else "❌"
            print(f"  {status_icon} {result['service']}: {result['status']}")

        # 功能测试结果
        function_tests = results["function_tests"]
        print(f"\n功能测试: {function_tests['successful_tests']}/{function_tests['total_tests']} 测试通过")

        for result in function_tests["results"]:
            if isinstance(result, dict):
                status_icon = "✅" if result.get("status") == "success" else "❌"
                test_name = result.get("test", "unknown")
                response_time = result.get("response_time", "N/A")
                print(f"  {status_icon} {test_name}: {result.get('status')} ({response_time})")
            else:
                print(f"  ❌ 测试异常: {str(result)}")

        # 性能测试结果
        performance = results["performance_test"]
        print(f"\n性能测试:")
        print(f"  总请求数: {performance['total_requests']}")
        print(f"  成功率: {performance['success_rate']}")
        print(f"  QPS: {performance['requests_per_second']}")
        print(f"  平均响应时间: {performance['average_response_time']}")

        print("\n" + "="*60)


async def main():
    """主函数"""
    tester = OptimizedServiceTester()

    try:
        # 运行所有测试
        results = await tester.run_all_tests()

        # 打印结果
        tester.print_test_results(results)

        # 保存结果到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"optimized_services_test_report_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n测试报告已保存到: {filename}")

        # 返回退出码
        health_check = results["health_check"]
        function_tests = results["function_tests"]

        if (health_check["healthy_services"] == health_check["total_services"] and
            function_tests["successful_tests"] == function_tests["total_tests"]):
            print("\n🎉 所有测试通过！")
            return 0
        else:
            print("\n⚠️  部分测试失败，请检查服务状态")
            return 1

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)