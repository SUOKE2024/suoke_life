"""
test_performance_optimization - 索克生活项目模块
"""

from pathlib import Path
from typing import Any
import aiohttp
import asyncio
import json
import logging
import sys
import time

#!/usr/bin/env python3
"""
小艾智能体性能优化测试脚本
验证优化后的性能提升
"""



# 添加项目路径
sys.path.insert(0, Path().resolve())

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# 使用loguru logger

class PerformanceTest:
    """性能测试类"""

    def __init__(self, base_url: str= "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = []

    async def setup(self):
        """设置测试环境"""
        self.session = aiohttp.ClientSession()

        # 等待服务启动
        for _ in range(30):
            try:
                async with self.session.get(f"{self.base_url}/api/v1/health/") as resp:
                    if resp.status == 200:
                        logger.info("服务已启动")
                        return
            except Exception:
                pass
            await asyncio.sleep(1)

        raise Exception("服务启动超时")

    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()

    async def measure_request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """测量单个请求的性能"""
        start_time = time.time()

        try:
            async with self.session.request(method, url, **kwargs) as resp:
                response_data = await resp.json()
                end_time = time.time()

                return {
                    "success": True,
                    "status_code": resp.status,
                    "response_time": end_time - start_time,
                    "response_data": response_data,
                    "cache_hit": response_data.get("data", {}).get("cache_hit", False)
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "error": str(e),
                "response_time": end_time - start_time,
                "cache_hit": False
            }

    async def test_device_status_caching(self, iterations: int = 10) -> dict[str, Any]:
        """测试设备状态缓存性能"""
        logger.info(f"测试设备状态缓存性能 ({iterations}次请求)")

        results = []
        url = f"{self.base_url}/api/v1/device/status"

        # 第一次请求(缓存未命中)
        result = await self.measure_request("GET", url)
        results.append(result)

        # 后续请求(应该命中缓存)
        for _ in range(iterations - 1):
            result = await self.measure_request("GET", url)
            results.append(result)
            await asyncio.sleep(0.1)  # 短暂延迟

        # 分析结果
        cache_hits = sum(1 for r in results if r.get("cache_hit", False))
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        cache_hit_times = [r["response_time"] for r in results if r.get("cache_hit", False)]
        cache_miss_times = [r["response_time"] for r in results if not r.get("cache_hit", False)]

        return {
            "test_name": "device_status_caching",
            "total_requests": len(results),
            "cache_hits": cache_hits,
            "cache_hit_rate": cache_hits / len(results),
            "avg_response_time": avg_response_time,
            "cache_hit_avg_time": sum(cache_hit_times) / len(cache_hit_times) if cache_hit_times else 0,
            "cache_miss_avg_time": sum(cache_miss_times) / len(cache_miss_times) if cache_miss_times else 0,
            "performance_improvement": (
                (sum(cache_miss_times) / len(cache_miss_times) - sum(cache_hit_times) / len(cache_hit_times))
                / (sum(cache_miss_times) / len(cache_miss_times)) * 100
                if cache_hit_times and cache_miss_times else 0
            )
        }

    async def test_concurrent_requests(self, concurrent_users: int = 10, requests_per_user: int = 5) -> dict[str, Any]:
        """测试并发请求性能"""
        logger.info(f"测试并发请求性能 ({concurrent_users}个并发用户,每用户{requests_per_user}个请求)")

        async def user_requests(user_id: int):
            """单个用户的请求"""
            user_results = []
            for _ in range(requests_per_user):
                # 混合不同类型的请求
                if i % 3 == 0:
                    url = f"{self.base_url}/api/v1/device/status"
                    result = await self.measure_request("GET", url)
                elif i % 3 == 1:
                    url = f"{self.base_url}/api/v1/device/capabilities"
                    result = await self.measure_request("GET", url)
                else:
                    url = f"{self.base_url}/api/v1/health/detailed"
                    result = await self.measure_request("GET", url)

                user_results.append(result)
                await asyncio.sleep(0.05)  # 模拟用户思考时间

            return user_results

        start_time = time.time()
        tasks = [user_requests(i) for _ in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        end_time = time.time()

        # 展平结果
        flat_results = [result for user_results in all_results for result in user_results]

        # 分析结果
        successful_requests = [r for r in flat_results if r["success"]]
        failed_requests = [r for r in flat_results if not r["success"]]

        return {
            "test_name": "concurrent_requests",
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": len(flat_results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / len(flat_results),
            "total_time": end_time - start_time,
            "requests_per_second": len(flat_results) / (end_time - start_time),
            "avg_response_time": sum(r["response_time"] for r in successful_requests) / len(successful_requests) if successful_requests else 0,
            "min_response_time": min(r["response_time"] for r in successful_requests) if successful_requests else 0,
            "max_response_time": max(r["response_time"] for r in successful_requests) if successful_requests else 0
        }

    async def test_cache_effectiveness(self) -> dict[str, Any]:
        """测试缓存有效性"""
        logger.info("测试缓存有效性")

        # 清空缓存
        await self.measure_request("DELETE", f"{self.base_url}/api/v1/device/cache")

        # 测试不同端点的缓存
        endpoints = [
            "/api/v1/device/status",
            "/api/v1/device/capabilities",
            "/api/v1/health/detailed"
        ]

        cache_results = {}

        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"

            # 第一次请求(缓存未命中)
            first_result = await self.measure_request("GET", url)

            # 第二次请求(应该命中缓存)
            second_result = await self.measure_request("GET", url)

            cache_results[endpoint] = {
                "first_request_time": first_result["response_time"],
                "second_request_time": second_result["response_time"],
                "cache_hit": second_result.get("cache_hit", False),
                "performance_improvement": (
                    (first_result["response_time"] - second_result["response_time"])
                    / first_result["response_time"] * 100
                    if first_result["response_time"] > 0 else 0
                )
            }

        return {
            "test_name": "cache_effectiveness",
            "endpoints": cache_results,
            "avg_improvement": sum(
                result["performance_improvement"]
                for result in cache_results.values()
            ) / len(cache_results)
        }

    async def test_memory_usage(self) -> dict[str, Any]:
        """测试内存使用情况"""
        logger.info("测试内存使用情况")

        # 获取初始内存状态
        initial_health = await self.measure_request("GET", f"{self.base_url}/api/v1/health/detailed")
        initial_memory = initial_health["response_data"]["data"]["system"]["memory"]["percent"]

        for _ in range(100):
            await self.measure_request("GET", f"{self.base_url}/api/v1/device/status")
            if i % 10 == 0:
                await asyncio.sleep(0.1)

        # 获取最终内存状态
        final_health = await self.measure_request("GET", f"{self.base_url}/api/v1/health/detailed")
        final_memory = final_health["response_data"]["data"]["system"]["memory"]["percent"]

        return {
            "test_name": "memory_usage",
            "initial_memory_percent": initial_memory,
            "final_memory_percent": final_memory,
            "memory_increase": final_memory - initial_memory,
            "memory_stable": abs(final_memory - initial_memory) < 5.0  # 5%以内认为稳定
        }

    async def run_all_tests(self) -> dict[str, Any]:
        """运行所有性能测试"""
        logger.info("开始性能优化测试")

        await self.setup()

        try:
            # 运行各项测试
            tests = [
                self.test_device_status_caching(),
                self.test_concurrent_requests(),
                self.test_cache_effectiveness(),
                self.test_memory_usage()
            ]

            results = await asyncio.gather(*tests)

            # 汇总结果
            summary = {
                "test_timestamp": time.time(),
                "test_results": results,
                "overall_performance": {
                    "cache_hit_rate": results[0]["cache_hit_rate"],
                    "concurrent_success_rate": results[1]["success_rate"],
                    "avg_cache_improvement": results[2]["avg_improvement"],
                    "memory_stable": results[3]["memory_stable"],
                    "requests_per_second": results[1]["requests_per_second"]
                }
            }

            return summary

        finally:
            await self.cleanup()

async def main():
    """主函数"""
    print("=" * 60)
    print("小艾智能体性能优化测试")
    print("=" * 60)

    # 检查服务是否运行
    test = PerformanceTest()

    try:
        results = await test.run_all_tests()

        # 输出结果
        print("\n测试结果:")
        print("-" * 40)

        for test_result in results["test_results"]:
            print(f"\n{test_result['test_name']}:")
            for key, value in test_result.items():
                if key != "test_name":
                    if isinstance(value, float):
                        print(f"  {key}: {value:.4f}")
                    else:
                        print(f"  {key}: {value}")

        print("\n整体性能指标:")
        print("-" * 40)
        overall = results["overall_performance"]
        print(f"缓存命中率: {overall['cache_hit_rate']:.2%}")
        print(f"并发成功率: {overall['concurrent_success_rate']:.2%}")
        print(f"平均缓存性能提升: {overall['avg_cache_improvement']:.2f}%")
        print(f"内存使用稳定: {'是' if overall['memory_stable'] else '否'}")
        print(f"每秒请求数: {overall['requests_per_second']:.2f}")

        # 性能评级
        score = 0
        if overall['cache_hit_rate'] > 0.8:
            score += 25
        if overall['concurrent_success_rate'] > 0.95:
            score += 25
        if overall['avg_cache_improvement'] > 30:
            score += 25
        if overall['memory_stable']:
            score += 25

        print(f"\n性能评分: {score}/100")
        if score >= 90:
            print("性能等级: 优秀 ⭐⭐⭐⭐⭐")
        elif score >= 70:
            print("性能等级: 良好 ⭐⭐⭐⭐")
        elif score >= 50:
            print("性能等级: 一般 ⭐⭐⭐")
        else:
            print("性能等级: 需要改进 ⭐⭐")

        # 保存详细结果
        with Path("performance_test_results.json").open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n详细结果已保存到: performance_test_results.json")

    except Exception as e:
        logger.error(f"测试失败: {e}")
        print(f"\n❌ 测试失败: {e}")
        print("\n请确保:")
        print("1. HTTP服务器正在运行 (python cmd/server/http_server.py)")
        print("2. 所有依赖已安装")
        print("3. 设备权限已配置")
        return 1

    print("\n✅ 性能优化测试完成!")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
