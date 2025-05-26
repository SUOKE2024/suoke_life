#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小艾服务无障碍功能性能测试
测试增强版客户端的性能改进效果
"""

import asyncio
import logging
import sys
import os
import time
import json
from typing import Dict, Any, List
import random

# 添加项目路径
sys.path.insert(0, os.path.abspath('.'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AccessibilityPerformanceTester:
    """无障碍功能性能测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.test_user_id = "perf_test_user_001"
        
    async def run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        logger.info("开始无障碍功能性能测试")
        
        test_results = {
            "timestamp": time.time(),
            "test_type": "accessibility_performance",
            "tests": {}
        }
        
        # 测试基础客户端性能
        test_results["tests"]["basic_client"] = await self._test_basic_client_performance()
        
        # 测试增强客户端性能
        test_results["tests"]["enhanced_client"] = await self._test_enhanced_client_performance()
        
        # 测试缓存效果
        test_results["tests"]["cache_performance"] = await self._test_cache_performance()
        
        # 测试连接池效果
        test_results["tests"]["connection_pool"] = await self._test_connection_pool_performance()
        
        # 测试降级机制
        test_results["tests"]["fallback_mechanism"] = await self._test_fallback_mechanism()
        
        # 计算性能改进
        test_results["performance_improvement"] = self._calculate_performance_improvement(test_results["tests"])
        
        # 保存测试结果
        with open("accessibility_performance_test_report.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
            
        self._print_performance_summary(test_results)
        
        return test_results
        
    async def _test_basic_client_performance(self) -> Dict[str, Any]:
        """测试基础客户端性能"""
        logger.info("测试基础客户端性能...")
        
        try:
            from xiaoai.integration.accessibility_client import AccessibilityServiceClient, AccessibilityConfig
            
            config = AccessibilityConfig(enabled=False)  # 测试模式
            client = AccessibilityServiceClient(config)
            
            # 模拟多次请求
            test_data = [
                b"test_audio_data_" + str(i).encode() for i in range(10)
            ]
            
            start_time = time.time()
            successful_requests = 0
            
            for audio_data in test_data:
                try:
                    result = client.process_voice_input(audio_data, self.test_user_id)
                    if result.get("status") in ["success", "mock"]:
                        successful_requests += 1
                except Exception as e:
                    logger.debug(f"基础客户端请求失败: {e}")
                    
            end_time = time.time()
            total_time = end_time - start_time
            
            return {
                "status": "completed",
                "total_requests": len(test_data),
                "successful_requests": successful_requests,
                "total_time": total_time,
                "average_time_per_request": total_time / len(test_data),
                "requests_per_second": len(test_data) / total_time if total_time > 0 else 0,
                "success_rate": successful_requests / len(test_data)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def _test_enhanced_client_performance(self) -> Dict[str, Any]:
        """测试增强客户端性能"""
        logger.info("测试增强客户端性能...")
        
        try:
            from xiaoai.integration.enhanced_accessibility_client import EnhancedAccessibilityClient
            from xiaoai.integration.accessibility_client import AccessibilityConfig
            
            config = AccessibilityConfig(enabled=False)  # 测试模式
            client = EnhancedAccessibilityClient(config)
            
            # 模拟多次请求
            test_data = [
                b"test_audio_data_" + str(i).encode() for i in range(10)
            ]
            
            start_time = time.time()
            successful_requests = 0
            
            for audio_data in test_data:
                try:
                    result = await client.process_voice_input(audio_data, self.test_user_id)
                    if result.get("status") in ["success", "fallback"]:
                        successful_requests += 1
                except Exception as e:
                    logger.debug(f"增强客户端请求失败: {e}")
                    
            end_time = time.time()
            total_time = end_time - start_time
            
            # 获取性能指标
            metrics = client.get_performance_metrics()
            
            # 清理资源
            client.close()
            
            return {
                "status": "completed",
                "total_requests": len(test_data),
                "successful_requests": successful_requests,
                "total_time": total_time,
                "average_time_per_request": total_time / len(test_data),
                "requests_per_second": len(test_data) / total_time if total_time > 0 else 0,
                "success_rate": successful_requests / len(test_data),
                "performance_metrics": metrics
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def _test_cache_performance(self) -> Dict[str, Any]:
        """测试缓存性能"""
        logger.info("测试缓存性能...")
        
        try:
            from xiaoai.integration.enhanced_accessibility_client import EnhancedAccessibilityClient
            from xiaoai.integration.accessibility_client import AccessibilityConfig
            
            config = AccessibilityConfig(enabled=False)
            client = EnhancedAccessibilityClient(config)
            
            # 相同的测试数据（应该被缓存）
            test_audio = b"cached_test_audio_data"
            
            # 第一次请求（无缓存）
            start_time = time.time()
            result1 = await client.process_voice_input(test_audio, self.test_user_id, use_cache=True)
            first_request_time = time.time() - start_time
            
            # 第二次请求（有缓存）
            start_time = time.time()
            result2 = await client.process_voice_input(test_audio, self.test_user_id, use_cache=True)
            second_request_time = time.time() - start_time
            
            # 第三次请求（禁用缓存）
            start_time = time.time()
            result3 = await client.process_voice_input(test_audio, self.test_user_id, use_cache=False)
            no_cache_request_time = time.time() - start_time
            
            metrics = client.get_performance_metrics()
            client.close()
            
            return {
                "status": "completed",
                "first_request_time": first_request_time,
                "cached_request_time": second_request_time,
                "no_cache_request_time": no_cache_request_time,
                "cache_speedup": first_request_time / second_request_time if second_request_time > 0 else 0,
                "cache_hits": metrics.get("cache_hits", 0),
                "cache_size": metrics.get("cache_size", 0)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def _test_connection_pool_performance(self) -> Dict[str, Any]:
        """测试连接池性能"""
        logger.info("测试连接池性能...")
        
        try:
            from xiaoai.integration.enhanced_accessibility_client import EnhancedAccessibilityClient
            from xiaoai.integration.accessibility_client import AccessibilityConfig
            
            config = AccessibilityConfig(enabled=False)
            client = EnhancedAccessibilityClient(config)
            
            # 并发请求测试
            async def make_request(i):
                audio_data = f"concurrent_test_{i}".encode()
                return await client.process_voice_input(audio_data, f"user_{i}")
                
            # 测试并发性能
            start_time = time.time()
            tasks = [make_request(i) for i in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("status") in ["success", "fallback"])
            
            metrics = client.get_performance_metrics()
            client.close()
            
            return {
                "status": "completed",
                "concurrent_requests": len(tasks),
                "successful_requests": successful_requests,
                "total_time": end_time - start_time,
                "pool_status": metrics.get("pool_status", {}),
                "success_rate": successful_requests / len(tasks)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    async def _test_fallback_mechanism(self) -> Dict[str, Any]:
        """测试降级机制"""
        logger.info("测试降级机制...")
        
        try:
            from xiaoai.integration.enhanced_accessibility_client import EnhancedAccessibilityClient
            from xiaoai.integration.accessibility_client import AccessibilityConfig
            
            # 模拟服务不可用的情况
            config = AccessibilityConfig(enabled=False)
            client = EnhancedAccessibilityClient(config)
            
            # 测试各种降级场景
            test_cases = [
                ("voice", b"fallback_test_audio"),
                ("image", b"fallback_test_image"),
                ("content", "fallback_test_content")
            ]
            
            fallback_results = []
            
            for test_type, test_data in test_cases:
                start_time = time.time()
                
                if test_type == "voice":
                    result = await client.process_voice_input(test_data, self.test_user_id)
                elif test_type == "image":
                    result = await client.process_image_input(test_data, self.test_user_id)
                elif test_type == "content":
                    result = await client.generate_accessible_content(test_data.decode(), "screen_reader", self.test_user_id)
                    
                response_time = time.time() - start_time
                
                fallback_results.append({
                    "test_type": test_type,
                    "response_time": response_time,
                    "status": result.get("status"),
                    "is_fallback": result.get("fallback", False)
                })
                
            client.close()
            
            return {
                "status": "completed",
                "fallback_tests": fallback_results,
                "all_fallbacks_working": all(r["is_fallback"] for r in fallback_results),
                "average_fallback_time": sum(r["response_time"] for r in fallback_results) / len(fallback_results)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def _calculate_performance_improvement(self, tests: Dict[str, Any]) -> Dict[str, Any]:
        """计算性能改进"""
        improvements = {}
        
        try:
            basic = tests.get("basic_client", {})
            enhanced = tests.get("enhanced_client", {})
            
            if basic.get("status") == "completed" and enhanced.get("status") == "completed":
                # 响应时间改进
                basic_avg_time = basic.get("average_time_per_request", 0)
                enhanced_avg_time = enhanced.get("average_time_per_request", 0)
                
                if basic_avg_time > 0:
                    improvements["response_time_improvement"] = (
                        (basic_avg_time - enhanced_avg_time) / basic_avg_time * 100
                    )
                    
                # 吞吐量改进
                basic_rps = basic.get("requests_per_second", 0)
                enhanced_rps = enhanced.get("requests_per_second", 0)
                
                if basic_rps > 0:
                    improvements["throughput_improvement"] = (
                        (enhanced_rps - basic_rps) / basic_rps * 100
                    )
                    
                # 成功率比较
                improvements["basic_success_rate"] = basic.get("success_rate", 0)
                improvements["enhanced_success_rate"] = enhanced.get("success_rate", 0)
                
            # 缓存效果
            cache_test = tests.get("cache_performance", {})
            if cache_test.get("status") == "completed":
                improvements["cache_speedup"] = cache_test.get("cache_speedup", 1)
                
            # 降级机制效果
            fallback_test = tests.get("fallback_mechanism", {})
            if fallback_test.get("status") == "completed":
                improvements["fallback_reliability"] = fallback_test.get("all_fallbacks_working", False)
                improvements["fallback_response_time"] = fallback_test.get("average_fallback_time", 0)
                
        except Exception as e:
            improvements["calculation_error"] = str(e)
            
        return improvements
        
    def _print_performance_summary(self, results: Dict[str, Any]):
        """打印性能测试总结"""
        print("\n" + "="*80)
        print("小艾服务无障碍功能性能测试报告")
        print("="*80)
        
        tests = results.get("tests", {})
        improvements = results.get("performance_improvement", {})
        
        # 基础性能对比
        print("\n📊 基础性能对比:")
        basic = tests.get("basic_client", {})
        enhanced = tests.get("enhanced_client", {})
        
        if basic.get("status") == "completed":
            print(f"  基础客户端:")
            print(f"    - 平均响应时间: {basic.get('average_time_per_request', 0):.4f}秒")
            print(f"    - 请求成功率: {basic.get('success_rate', 0):.2%}")
            print(f"    - 每秒请求数: {basic.get('requests_per_second', 0):.2f}")
            
        if enhanced.get("status") == "completed":
            print(f"  增强客户端:")
            print(f"    - 平均响应时间: {enhanced.get('average_time_per_request', 0):.4f}秒")
            print(f"    - 请求成功率: {enhanced.get('success_rate', 0):.2%}")
            print(f"    - 每秒请求数: {enhanced.get('requests_per_second', 0):.2f}")
            
        # 性能改进
        print("\n🚀 性能改进:")
        if "response_time_improvement" in improvements:
            print(f"  - 响应时间改进: {improvements['response_time_improvement']:.1f}%")
        if "throughput_improvement" in improvements:
            print(f"  - 吞吐量改进: {improvements['throughput_improvement']:.1f}%")
            
        # 缓存效果
        cache_test = tests.get("cache_performance", {})
        if cache_test.get("status") == "completed":
            print(f"\n💾 缓存效果:")
            print(f"  - 缓存加速比: {cache_test.get('cache_speedup', 1):.1f}x")
            print(f"  - 缓存命中数: {cache_test.get('cache_hits', 0)}")
            
        # 降级机制
        fallback_test = tests.get("fallback_mechanism", {})
        if fallback_test.get("status") == "completed":
            print(f"\n🛡️ 降级机制:")
            print(f"  - 降级可靠性: {'✅ 正常' if fallback_test.get('all_fallbacks_working') else '❌ 异常'}")
            print(f"  - 降级响应时间: {fallback_test.get('average_fallback_time', 0):.4f}秒")
            
        print(f"\n📄 详细报告已保存到: accessibility_performance_test_report.json")
        print("="*80)

async def main():
    """主函数"""
    tester = AccessibilityPerformanceTester()
    await tester.run_performance_tests()

if __name__ == "__main__":
    asyncio.run(main()) 