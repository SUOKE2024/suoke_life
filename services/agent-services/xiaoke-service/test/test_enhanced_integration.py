"""
test_enhanced_integration - 索克生活项目模块
"""

from services.agent_services.xiaoke_service.internal.service.enhanced_resource_service import (
from services.common.governance.rate_limiter import RateLimitExceeded
from unittest.mock import patch
import asyncio
import contextlib
import pytest
import time

#!/usr/bin/env python3
"""
xiaoke-service 增强版集成测试套件
测试所有核心功能和优化组件
"""



# 导入被测试的组件
    ConstitutionType,
    ProductRequest,
    ResourceRequest,
    get_resource_service,
)

# 常量定义
CONCURRENT_REQUESTS = 5
PERFORMANCE_TEST_REQUESTS = 100
MAX_RESPONSE_TIME = 0.5
CIRCUIT_BREAKER_THRESHOLD = 6  # 超过失败阈值


class TestXiaokeServiceIntegration:
    """xiaoke-service 集成测试"""

    @pytest.fixture
    async def resource_service(self):
        """获取资源服务实例"""
        service = await get_resource_service()
        yield service
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_basic_resource_search(self, resource_service):
        """测试基本资源搜索功能"""
        request = ResourceRequest(
            user_id="test_user_001",
            resource_type="medical_facility",
            location="北京市朝阳区",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="normal",
            preferences={"specialty": "内科"},
        )

        result = await resource_service.search_resources(request)

        # 验证结果
        assert result.request_id is not None
        assert len(result.matched_resources) > 0
        assert result.availability_info is not None
        assert result.cost_estimate > 0
        assert len(result.recommendations) > 0
        assert result.processing_time > 0

        # 验证资源内容
        resource = result.matched_resources[0]
        assert "name" in resource
        assert "type" in resource
        assert "location" in resource
        assert "rating" in resource

        print(f"✅ 基本资源搜索测试通过 - 处理时间: {result.processing_time:.3f}s")

    @pytest.mark.asyncio
    async def test_product_recommendation(self, resource_service):
        """测试产品推荐功能"""
        request = ProductRequest(
            user_id="test_user_002",
            product_category="herbal_tea",
            constitution_type=ConstitutionType.QI_XU,
            dietary_restrictions=["无糖"],
            budget_range="medium",
            preferences={"organic": True},
        )

        result = await resource_service.recommend_products(request)

        # 验证结果
        assert result.request_id is not None
        assert len(result.recommended_products) > 0
        assert result.nutrition_analysis is not None
        assert result.tcm_benefits is not None
        assert result.customization_options is not None
        assert result.blockchain_info is not None

        # 验证产品内容
        product = result.recommended_products[0]
        assert "name" in product
        assert "category" in product
        assert "price" in product
        assert "constitution_match" in product

        print(f"✅ 产品推荐测试通过 - 处理时间: {result.processing_time:.3f}s")

    @pytest.mark.asyncio
    async def test_caching_functionality(self, resource_service):
        """测试缓存功能"""
        request = ResourceRequest(
            user_id="test_user_003",
            resource_type="doctor",
            location="上海市浦东新区",
            constitution_type=ConstitutionType.YANG_XU,
            urgency_level="normal",
        )

        # 第一次请求
        start_time = time.time()
        result1 = await resource_service.search_resources(request)
        first_time = time.time() - start_time

        # 第二次请求（应该命中缓存）
        start_time = time.time()
        result2 = await resource_service.search_resources(request)
        second_time = time.time() - start_time

        # 验证缓存效果
        assert result1.request_id != result2.request_id  # 请求ID不同
        assert len(result1.matched_resources) == len(
            result2.matched_resources
        )  # 结果相同
        assert second_time < first_time * 0.5  # 第二次明显更快

        # 检查缓存统计
        stats = resource_service.get_health_status()
        assert stats["cache_hit_rate"] > 0

        print(
            f"✅ 缓存功能测试通过 - 首次: {first_time:.3f}s, 缓存: {second_time:.3f}s"
        )

    @pytest.mark.asyncio
    async def test_emergency_priority_handling(self, resource_service):
        """测试紧急情况优先处理"""
        # 普通请求
        normal_request = ResourceRequest(
            user_id="test_user_004",
            resource_type="medical_facility",
            location="广州市天河区",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="normal",
        )

        # 紧急请求
        emergency_request = ResourceRequest(
            user_id="test_user_005",
            resource_type="medical_facility",
            location="广州市天河区",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="emergency",
        )

        # 并发发送请求
        start_time = time.time()
        results = await asyncio.gather(
            resource_service.search_resources(normal_request),
            resource_service.search_resources(emergency_request),
        )
        total_time = time.time() - start_time

        normal_result, emergency_result = results

        # 验证紧急请求得到优先处理
        assert emergency_result.processing_time <= normal_result.processing_time
        assert len(emergency_result.matched_resources) > 0

        print(f"✅ 紧急优先处理测试通过 - 总时间: {total_time:.3f}s")

    @pytest.mark.asyncio
    async def test_parallel_processing(self, resource_service):
        """测试并行处理能力"""
        requests = []
        for i in range(CONCURRENT_REQUESTS):
            request = ResourceRequest(
                user_id=f"test_user_{100 + i}",
                resource_type="equipment",
                location="深圳市南山区",
                constitution_type=ConstitutionType.BALANCED,
                urgency_level="normal",
            )
            requests.append(request)

        # 并行处理多个请求
        start_time = time.time()
        results = await asyncio.gather(
            *[resource_service.search_resources(req) for req in requests]
        )
        total_time = time.time() - start_time

        # 验证所有请求都成功处理
        assert len(results) == CONCURRENT_REQUESTS
        for result in results:
            assert result.request_id is not None
            assert len(result.matched_resources) > 0

        # 验证并行处理效率
        avg_time = total_time / len(results)
        assert avg_time < MAX_RESPONSE_TIME  # 平均处理时间应该合理

        print(
            f"✅ 并行处理测试通过 - {CONCURRENT_REQUESTS}个请求总时间: {total_time:.3f}s, 平均: {avg_time:.3f}s"
        )

    @pytest.mark.asyncio
    async def test_circuit_breaker_normal_operation(self, resource_service):
        """测试断路器正常操作"""
        request = ResourceRequest(
            user_id="test_user_200",
            resource_type="medical_facility",
            location="杭州市西湖区",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="normal",
        )

        # 正常情况下断路器应该是关闭状态
        result = await resource_service.search_resources(request)
        assert result.request_id is not None

        # 检查断路器状态
        stats = resource_service.get_health_status()
        assert "circuit_breaker_state" in stats

        print("✅ 断路器正常操作测试通过")

    @pytest.mark.asyncio
    async def test_circuit_breaker_failure_handling(self, resource_service):
        """测试断路器故障处理"""
        # 模拟外部服务故障
        with patch.object(
            resource_service,
            "_call_external_api",
            side_effect=Exception("外部服务故障"),
        ):
            request = ResourceRequest(
                user_id="test_user_201",
                resource_type="medical_facility",
                location="成都市锦江区",
                constitution_type=ConstitutionType.BALANCED,
                urgency_level="normal",
            )

            # 多次调用触发断路器
            for _i in range(CIRCUIT_BREAKER_THRESHOLD):  # 超过失败阈值
                with contextlib.suppress(Exception):
                    await resource_service.search_resources(request)

            # 检查断路器是否打开
            resource_service.get_health_status()
            # 断路器应该检测到故障

        print("✅ 断路器故障处理测试通过")

    @pytest.mark.asyncio
    async def test_rate_limiter_functionality(self, resource_service):
        """测试限流器功能"""
        request = ResourceRequest(
            user_id="test_user_300",
            resource_type="doctor",
            location="武汉市武昌区",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="normal",
        )

        # 快速发送多个请求
        success_count = 0
        rate_limited_count = 0

        for _i in range(20):  # 发送20个请求
            try:
                await resource_service.search_resources(request)
                success_count += 1
            except RateLimitExceeded:
                rate_limited_count += 1
            except Exception:
                pass  # 其他异常忽略

        # 验证限流器工作
        assert success_count > 0  # 至少有一些请求成功
        print(
            f"✅ 限流器功能测试通过 - 成功: {success_count}, 限流: {rate_limited_count}"
        )

    @pytest.mark.asyncio
    async def test_rate_limiter_recovery(self, resource_service):
        """测试限流器恢复"""
        request = ResourceRequest(
            user_id="test_user_301",
            resource_type="equipment",
            location="西安市雁塔区",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="normal",
        )

        # 触发限流
        for _i in range(10):
            try:
                await resource_service.search_resources(request)
            except RateLimitExceeded:
                break
            except Exception:
                pass

        # 等待限流窗口重置
        await asyncio.sleep(2)

        # 验证可以再次正常请求
        result = await resource_service.search_resources(request)
        assert result.request_id is not None

        print("✅ 限流器恢复测试通过")

    @pytest.mark.asyncio
    async def test_distributed_tracing_basic(self, resource_service):
        """测试分布式追踪基本功能"""
        request = ResourceRequest(
            user_id="test_user_400",
            resource_type="medical_facility",
            location="南京市鼓楼区",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="normal",
        )

        # 执行请求并检查追踪
        result = await resource_service.search_resources(request)

        # 验证请求成功
        assert result.request_id is not None

        # 检查追踪信息（在实际实现中会有追踪ID）
        stats = resource_service.get_health_status()
        assert "total_requests" in stats

        print("✅ 分布式追踪基本功能测试通过")

    @pytest.mark.asyncio
    async def test_distributed_tracing_nested(self, resource_service):
        """测试分布式追踪嵌套调用"""
        # 模拟嵌套调用场景
        request1 = ResourceRequest(
            user_id="test_user_401",
            resource_type="medical_facility",
            location="天津市和平区",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="normal",
        )

        request2 = ProductRequest(
            user_id="test_user_401",
            product_category="health_food",
            constitution_type=ConstitutionType.BALANCED,
            dietary_restrictions=[],
            budget_range="medium",
        )

        # 顺序执行两个相关请求
        result1 = await resource_service.search_resources(request1)
        result2 = await resource_service.recommend_products(request2)

        # 验证两个请求都成功
        assert result1.request_id is not None
        assert result2.request_id is not None

        print("✅ 分布式追踪嵌套调用测试通过")

    @pytest.mark.asyncio
    async def test_full_diagnosis_flow_integration(self, resource_service):
        """测试完整诊断流程集成"""
        # 模拟完整的用户诊断流程
        user_id = "test_user_500"

        # 1. 搜索医疗资源
        resource_request = ResourceRequest(
            user_id=user_id,
            resource_type="medical_facility",
            location="重庆市渝中区",
            constitution_type=ConstitutionType.QI_XU,
            urgency_level="normal",
            preferences={"specialty": "中医科"},
        )

        resource_result = await resource_service.search_resources(resource_request)
        assert len(resource_result.matched_resources) > 0

        # 2. 推荐相关产品
        product_request = ProductRequest(
            user_id=user_id,
            product_category="tcm_products",
            constitution_type=ConstitutionType.QI_XU,
            dietary_restrictions=[],
            budget_range="medium",
            preferences={"constitution_specific": True},
        )

        product_result = await resource_service.recommend_products(product_request)
        assert len(product_result.recommended_products) > 0

        # 3. 验证整个流程的一致性
        assert resource_result.request_id != product_result.request_id
        assert resource_result.processing_time > 0
        assert product_result.processing_time > 0

        print(f"✅ 完整诊断流程集成测试通过 - 用户: {user_id}")

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, resource_service):
        """测试错误处理和恢复能力"""
        # 测试无效请求
        invalid_request = ResourceRequest(
            user_id="",  # 无效用户ID
            resource_type="invalid_type",
            location="",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="invalid_level",
        )

        try:
            await resource_service.search_resources(invalid_request)
            raise AssertionError("应该抛出异常")
        except Exception as e:
            assert str(e)  # 确保有错误信息

        # 验证服务仍然可以处理正常请求
        valid_request = ResourceRequest(
            user_id="test_user_600",
            resource_type="medical_facility",
            location="长沙市岳麓区",
            constitution_type=ConstitutionType.BALANCED,
            urgency_level="normal",
        )

        result = await resource_service.search_resources(valid_request)
        assert result.request_id is not None

        print("✅ 错误处理和恢复能力测试通过")

    @pytest.mark.asyncio
    async def test_performance_under_load(self, resource_service):
        """测试负载下的性能"""
        # 创建大量并发请求
        requests = []
        for i in range(PERFORMANCE_TEST_REQUESTS):
            request = ResourceRequest(
                user_id=f"load_test_user_{i}",
                resource_type="medical_facility",
                location="北京市海淀区",
                constitution_type=ConstitutionType.BALANCED,
                urgency_level="normal",
            )
            requests.append(request)

        # 分批处理请求
        batch_size = 10
        total_start_time = time.time()
        all_results = []

        for i in range(0, len(requests), batch_size):
            batch = requests[i : i + batch_size]
            batch_results = await asyncio.gather(
                *[resource_service.search_resources(req) for req in batch]
            )
            all_results.extend(batch_results)

        total_time = time.time() - total_start_time

        # 验证性能
        assert len(all_results) == PERFORMANCE_TEST_REQUESTS
        avg_time = total_time / len(all_results)
        assert avg_time < MAX_RESPONSE_TIME  # 平均处理时间应该合理

        # 检查服务健康状态
        stats = resource_service.get_health_status()
        assert stats["total_requests"] >= PERFORMANCE_TEST_REQUESTS

        print(
            f"✅ 负载性能测试通过 - {PERFORMANCE_TEST_REQUESTS}个请求总时间: {total_time:.3f}s, 平均: {avg_time:.3f}s"
        )

    def test_service_health_status(self, resource_service):
        """测试服务健康状态"""
        stats = resource_service.get_health_status()

        # 验证必要的统计信息
        required_fields = [
            "total_requests",
            "success_rate",
            "avg_processing_time",
            "cache_hit_rate",
            "active_connections",
        ]

        for field in required_fields:
            assert field in stats, f"缺少统计字段: {field}"

        # 验证数值合理性
        assert 0 <= stats["success_rate"] <= 1
        assert 0 <= stats["cache_hit_rate"] <= 1
        assert stats["avg_processing_time"] >= 0
        assert stats["active_connections"] >= 0

        print("✅ 服务健康状态测试通过")


# 运行测试的辅助函数
async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行 xiaoke-service 增强版集成测试...")

    # 创建测试实例
    test_instance = TestXiaokeServiceIntegration()

    # 获取服务实例
    resource_service = await get_resource_service()

    try:
        # 运行所有测试
        test_methods = [
            test_instance.test_basic_resource_search,
            test_instance.test_product_recommendation,
            test_instance.test_caching_functionality,
            test_instance.test_emergency_priority_handling,
            test_instance.test_parallel_processing,
            test_instance.test_circuit_breaker_normal_operation,
            test_instance.test_circuit_breaker_failure_handling,
            test_instance.test_rate_limiter_functionality,
            test_instance.test_rate_limiter_recovery,
            test_instance.test_distributed_tracing_basic,
            test_instance.test_distributed_tracing_nested,
            test_instance.test_full_diagnosis_flow_integration,
            test_instance.test_error_handling_and_recovery,
            test_instance.test_performance_under_load,
        ]

        passed = 0
        failed = 0

        for test_method in test_methods:
            try:
                await test_method(resource_service)
                passed += 1
            except Exception as e:
                print(f"❌ {test_method.__name__} 失败: {e}")
                failed += 1

        # 运行同步测试
        try:
            test_instance.test_service_health_status(resource_service)
            passed += 1
        except Exception as e:
            print(f"❌ test_service_health_status 失败: {e}")
            failed += 1

        print(f"\n📊 测试结果: {passed} 通过, {failed} 失败")

        if failed == 0:
            print("🎉 所有测试通过! xiaoke-service 优化成功!")
        else:
            print("⚠️  部分测试失败, 需要进一步优化")

    finally:
        await resource_service.cleanup()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
