#!/usr/bin/env python

"""
智能体无障碍服务集成测试
测试四个智能体（小艾、小克、老克、索儿）与无障碍服务的集成功能
"""

import asyncio
import logging
import os
import sys
import time
from typing import Any, Dict

# 添加路径以导入智能体服务
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agent-services"))

# 导入智能体服务实现
try:
    from laoke_service.internal.service.laoke_service_impl import LaokeServiceImpl
    from soer_service.internal.service.soer_service_impl import SoerServiceImpl
    from xiaoai_service.internal.service.xiaoai_service_impl import XiaoaiServiceImpl
    from xiaoke_service.internal.service.xiaoke_service_impl import XiaokeServiceImpl
except ImportError as e:
    print(f"导入智能体服务失败: {e}")
    print("请确保智能体服务模块路径正确")

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AgentAccessibilityIntegrationTest:
    """智能体无障碍服务集成测试类"""

    def __init__(self) -> None:
        """初始化测试环境"""
        self.config = {
            "accessibility_service": {
                "host": "localhost",
                "port": 50051,
                "timeout": 30,
            },
            "test_user_id": "test_user_001",
        }

        # 初始化智能体服务
        self.xiaoai_service = None
        self.xiaoke_service = None
        self.laoke_service = None
        self.soer_service = None

        logger.info("智能体无障碍服务集成测试初始化完成")

    async def setup_services(self) -> None:
        """设置智能体服务"""
        try:
            self.xiaoai_service = XiaoaiServiceImpl(self.config)
            self.xiaoke_service = XiaokeServiceImpl(self.config)
            self.laoke_service = LaokeServiceImpl(self.config)
            self.soer_service = SoerServiceImpl(self.config)

            logger.info("所有智能体服务初始化完成")
            return True

        except Exception as e:
            logger.error(f"智能体服务初始化失败: {e}")
            return False

    async def test_xiaoai_accessibility_features(self) -> dict[str, Any]:
        """测试小艾智能体的无障碍功能"""
        logger.info("开始测试小艾智能体无障碍功能")

        test_results = {
            "service_name": "小艾智能体",
            "tests": {},
            "overall_success": True,
        }

        try:
            # 测试四诊协调无障碍功能
            diagnosis_request = {
                "patient_info": {
                    "age": 35,
                    "gender": "female",
                    "symptoms": ["头痛", "失眠", "食欲不振"],
                },
                "diagnosis_type": "comprehensive",
            }

            diagnosis_result = (
                await self.xiaoai_service.coordinate_four_diagnoses_accessible(
                    diagnosis_request, self.config["test_user_id"], {"format": "audio"}
                )
            )

            test_results["tests"]["four_diagnoses"] = {
                "success": diagnosis_result.get("success", False),
                "has_accessible_content": "accessible_content" in diagnosis_result,
                "error": diagnosis_result.get("error"),
            }

            # 测试多模态输入处理无障碍功能
            multimodal_request = {
                "input_data": {
                    "text": "我最近感觉很疲劳",
                    "voice_data": b"mock_voice_data",
                    "image_data": b"mock_image_data",
                },
                "input_types": ["text", "voice", "image"],
            }

            multimodal_result = (
                await self.xiaoai_service.process_multimodal_input_accessible(
                    multimodal_request,
                    self.config["test_user_id"],
                    {"format": "simplified"},
                )
            )

            test_results["tests"]["multimodal_input"] = {
                "success": multimodal_result.get("success", False),
                "has_accessible_content": "accessible_content" in multimodal_result,
                "error": multimodal_result.get("error"),
            }

            # 测试健康记录查询无障碍功能
            records_request = {
                "query_type": "recent",
                "time_range": "30_days",
                "categories": ["diagnosis", "treatment", "medication"],
            }

            records_result = await self.xiaoai_service.query_health_records_accessible(
                records_request, self.config["test_user_id"], {"format": "braille"}
            )

            test_results["tests"]["health_records"] = {
                "success": records_result.get("success", False),
                "has_accessible_content": "accessible_content" in records_result,
                "error": records_result.get("error"),
            }

        except Exception as e:
            logger.error(f"小艾智能体测试失败: {e}")
            test_results["overall_success"] = False
            test_results["error"] = str(e)

        # 检查整体成功率
        if test_results["tests"]:
            success_count = sum(
                1 for test in test_results["tests"].values() if test["success"]
            )
            test_results["success_rate"] = success_count / len(test_results["tests"])
            test_results["overall_success"] = test_results["success_rate"] > 0.5

        logger.info(
            f"小艾智能体测试完成，成功率: {test_results.get('success_rate', 0):.2%}"
        )
        return test_results

    async def test_xiaoke_accessibility_features(self) -> dict[str, Any]:
        """测试小克智能体的无障碍功能"""
        logger.info("开始测试小克智能体无障碍功能")

        test_results = {
            "service_name": "小克智能体",
            "tests": {},
            "overall_success": True,
        }

        try:
            # 测试医疗资源调度无障碍功能
            resource_request = {
                "resource_type": "doctor_appointment",
                "specialty": "中医内科",
                "preferred_time": "2024-01-25 14:00",
                "location": "北京市朝阳区",
            }

            resource_result = (
                await self.xiaoke_service.schedule_medical_resources_accessible(
                    resource_request, self.config["test_user_id"], {"format": "audio"}
                )
            )

            test_results["tests"]["medical_resources"] = {
                "success": resource_result.get("success", False),
                "has_accessible_content": "accessible_content" in resource_result,
                "error": resource_result.get("error"),
            }

            # 测试农产品定制无障碍功能
            product_request = {
                "product_type": "herbal_tea",
                "constitution_type": "阴虚质",
                "preferences": ["有机", "无添加"],
                "quantity": 1,
            }

            product_result = (
                await self.xiaoke_service.customize_agricultural_products_accessible(
                    product_request,
                    self.config["test_user_id"],
                    {"format": "simplified"},
                )
            )

            test_results["tests"]["agricultural_products"] = {
                "success": product_result.get("success", False),
                "has_accessible_content": "accessible_content" in product_result,
                "error": product_result.get("error"),
            }

            # 测试支付处理无障碍功能
            payment_request = {
                "amount": 299.00,
                "currency": "CNY",
                "payment_method": "wechat_pay",
                "order_id": "order_001",
            }

            payment_result = await self.xiaoke_service.process_payment_accessible(
                payment_request, self.config["test_user_id"], {"format": "audio"}
            )

            test_results["tests"]["payment_processing"] = {
                "success": payment_result.get("success", False),
                "has_accessible_content": "accessible_content" in payment_result,
                "error": payment_result.get("error"),
            }

        except Exception as e:
            logger.error(f"小克智能体测试失败: {e}")
            test_results["overall_success"] = False
            test_results["error"] = str(e)

        # 检查整体成功率
        if test_results["tests"]:
            success_count = sum(
                1 for test in test_results["tests"].values() if test["success"]
            )
            test_results["success_rate"] = success_count / len(test_results["tests"])
            test_results["overall_success"] = test_results["success_rate"] > 0.5

        logger.info(
            f"小克智能体测试完成，成功率: {test_results.get('success_rate', 0):.2%}"
        )
        return test_results

    async def test_laoke_accessibility_features(self) -> dict[str, Any]:
        """测试老克智能体的无障碍功能"""
        logger.info("开始测试老克智能体无障碍功能")

        test_results = {
            "service_name": "老克智能体",
            "tests": {},
            "overall_success": True,
        }

        try:
            # 测试知识图谱检索无障碍功能
            search_request = {
                "query": "中医四诊法",
                "categories": ["中医基础", "诊断方法"],
                "difficulty_level": "初级",
            }

            search_result = await self.laoke_service.search_knowledge_accessible(
                search_request, self.config["test_user_id"], {"format": "audio"}
            )

            test_results["tests"]["knowledge_search"] = {
                "success": search_result.get("success", False),
                "has_accessible_content": "accessible_content" in search_result,
                "error": search_result.get("error"),
            }

            # 测试学习路径无障碍功能
            path_request = {
                "learning_goal": "中医基础入门",
                "current_level": "初学者",
                "time_commitment": "每周3小时",
            }

            path_result = await self.laoke_service.get_learning_path_accessible(
                path_request, self.config["test_user_id"], {"format": "simplified"}
            )

            test_results["tests"]["learning_path"] = {
                "success": path_result.get("success", False),
                "has_accessible_content": "accessible_content" in path_result,
                "error": path_result.get("error"),
            }

            # 测试教育内容手语转换
            content_request = {
                "content": "中医四诊法包括望、闻、问、切四种诊断方法",
                "content_type": "lesson",
            }

            sign_result = await self.laoke_service.convert_educational_content_to_sign_language_accessible(
                content_request, self.config["test_user_id"]
            )

            test_results["tests"]["sign_language_conversion"] = {
                "success": sign_result.get("success", False),
                "has_sign_language_result": "sign_language_result" in sign_result,
                "error": sign_result.get("error"),
            }

        except Exception as e:
            logger.error(f"老克智能体测试失败: {e}")
            test_results["overall_success"] = False
            test_results["error"] = str(e)

        # 检查整体成功率
        if test_results["tests"]:
            success_count = sum(
                1 for test in test_results["tests"].values() if test["success"]
            )
            test_results["success_rate"] = success_count / len(test_results["tests"])
            test_results["overall_success"] = test_results["success_rate"] > 0.5

        logger.info(
            f"老克智能体测试完成，成功率: {test_results.get('success_rate', 0):.2%}"
        )
        return test_results

    async def test_soer_accessibility_features(self) -> dict[str, Any]:
        """测试索儿智能体的无障碍功能"""
        logger.info("开始测试索儿智能体无障碍功能")

        test_results = {
            "service_name": "索儿智能体",
            "tests": {},
            "overall_success": True,
        }

        try:
            # 测试健康计划生成无障碍功能
            plan_request = {
                "plan_type": "weight_loss",
                "duration": "30天",
                "goals": ["减重5kg", "改善睡眠", "增强体质"],
            }

            plan_result = await self.soer_service.generate_health_plan_accessible(
                plan_request, self.config["test_user_id"], {"format": "audio"}
            )

            test_results["tests"]["health_plan"] = {
                "success": plan_result.get("success", False),
                "has_accessible_content": "accessible_content" in plan_result,
                "error": plan_result.get("error"),
            }

            # 测试传感器数据分析无障碍功能
            sensor_request = {
                "sensor_data": {
                    "heart_rate": [72, 68, 70],
                    "steps": [8500, 9200, 7800],
                    "sleep_hours": [7.5, 8.0, 7.2],
                },
                "data_type": "daily_summary",
            }

            sensor_result = await self.soer_service.analyze_sensor_data_accessible(
                sensor_request, self.config["test_user_id"], {"format": "simplified"}
            )

            test_results["tests"]["sensor_analysis"] = {
                "success": sensor_result.get("success", False),
                "has_accessible_content": "accessible_content" in sensor_result,
                "error": sensor_result.get("error"),
            }

            # 测试营养追踪无障碍功能
            nutrition_request = {
                "food_items": [
                    {"name": "苹果", "quantity": 1, "unit": "个"},
                    {"name": "鸡胸肉", "quantity": 100, "unit": "g"},
                ],
                "meal_type": "lunch",
            }

            nutrition_result = await self.soer_service.track_nutrition_accessible(
                nutrition_request, self.config["test_user_id"], {"format": "braille"}
            )

            test_results["tests"]["nutrition_tracking"] = {
                "success": nutrition_result.get("success", False),
                "has_accessible_content": "accessible_content" in nutrition_result,
                "error": nutrition_result.get("error"),
            }

            # 测试情绪分析无障碍功能
            emotion_request = {
                "emotion_data": {"mood_score": 7, "stress_level": 3, "energy_level": 6},
                "analysis_type": "daily",
            }

            emotion_result = await self.soer_service.analyze_emotion_accessible(
                emotion_request, self.config["test_user_id"], {"format": "audio"}
            )

            test_results["tests"]["emotion_analysis"] = {
                "success": emotion_result.get("success", False),
                "has_accessible_content": "accessible_content" in emotion_result,
                "error": emotion_result.get("error"),
            }

        except Exception as e:
            logger.error(f"索儿智能体测试失败: {e}")
            test_results["overall_success"] = False
            test_results["error"] = str(e)

        # 检查整体成功率
        if test_results["tests"]:
            success_count = sum(
                1 for test in test_results["tests"].values() if test["success"]
            )
            test_results["success_rate"] = success_count / len(test_results["tests"])
            test_results["overall_success"] = test_results["success_rate"] > 0.5

        logger.info(
            f"索儿智能体测试完成，成功率: {test_results.get('success_rate', 0):.2%}"
        )
        return test_results

    async def run_comprehensive_test(self) -> dict[str, Any]:
        """运行综合测试"""
        logger.info("开始运行智能体无障碍服务综合集成测试")

        # 设置服务
        setup_success = await self.setup_services()
        if not setup_success:
            return {
                "overall_success": False,
                "error": "智能体服务初始化失败",
                "test_results": [],
            }

        # 运行各智能体测试
        test_results = []

        try:
            # 测试小艾智能体
            xiaoai_result = await self.test_xiaoai_accessibility_features()
            test_results.append(xiaoai_result)

            # 测试小克智能体
            xiaoke_result = await self.test_xiaoke_accessibility_features()
            test_results.append(xiaoke_result)

            # 测试老克智能体
            laoke_result = await self.test_laoke_accessibility_features()
            test_results.append(laoke_result)

            # 测试索儿智能体
            soer_result = await self.test_soer_accessibility_features()
            test_results.append(soer_result)

        except Exception as e:
            logger.error(f"综合测试执行失败: {e}")
            return {
                "overall_success": False,
                "error": str(e),
                "test_results": test_results,
            }

        # 计算整体成功率
        total_tests = sum(len(result.get("tests", {})) for result in test_results)
        successful_tests = sum(
            sum(
                1
                for test in result.get("tests", {}).values()
                if test.get("success", False)
            )
            for result in test_results
        )

        overall_success_rate = successful_tests / total_tests if total_tests > 0 else 0
        overall_success = overall_success_rate > 0.7  # 70%以上认为成功

        comprehensive_result = {
            "overall_success": overall_success,
            "overall_success_rate": overall_success_rate,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "test_results": test_results,
            "summary": {
                "xiaoai_success": xiaoai_result.get("overall_success", False),
                "xiaoke_success": xiaoke_result.get("overall_success", False),
                "laoke_success": laoke_result.get("overall_success", False),
                "soer_success": soer_result.get("overall_success", False),
            },
            "test_time": time.time(),
        }

        logger.info(f"综合测试完成，整体成功率: {overall_success_rate:.2%}")
        return comprehensive_result

    def cleanup(self) -> None:
        """清理资源"""
        try:
            if self.xiaoai_service:
                self.xiaoai_service.close()
            if self.xiaoke_service:
                self.xiaoke_service.close()
            if self.laoke_service:
                self.laoke_service.close()
            if self.soer_service:
                self.soer_service.close()

            logger.info("资源清理完成")
        except Exception as e:
            logger.error(f"资源清理失败: {e}")


def print_test_results(results: dict[str, Any]):
    """打印测试结果"""
    print("\n" + "=" * 80)
    print("智能体无障碍服务集成测试结果")
    print("=" * 80)

    print(f"整体成功: {'✅' if results['overall_success'] else '❌'}")
    print(f"整体成功率: {results.get('overall_success_rate', 0):.2%}")
    print(f"总测试数: {results.get('total_tests', 0)}")
    print(f"成功测试数: {results.get('successful_tests', 0)}")

    print("\n各智能体测试结果:")
    print("-" * 40)

    for result in results.get("test_results", []):
        service_name = result.get("service_name", "未知服务")
        success = result.get("overall_success", False)
        success_rate = result.get("success_rate", 0)

        print(
            f"{service_name}: {'✅' if success else '❌'} (成功率: {success_rate:.2%})"
        )

        # 打印详细测试结果
        for test_name, test_result in result.get("tests", {}).items():
            test_success = test_result.get("success", False)
            print(f"  - {test_name}: {'✅' if test_success else '❌'}")
            if not test_success and test_result.get("error"):
                print(f"    错误: {test_result['error']}")

    print("\n" + "=" * 80)


async def main() -> None:
    """主函数"""
    test_runner = AgentAccessibilityIntegrationTest()

    try:
        # 运行综合测试
        results = await test_runner.run_comprehensive_test()

        # 打印结果
        print_test_results(results)

        # 返回适当的退出码
        return 0 if results["overall_success"] else 1

    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        print(f"\n❌ 测试执行失败: {e}")
        return 1

    finally:
        # 清理资源
        test_runner.cleanup()


if __name__ == "__main__":
    # 运行测试
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
