#!/usr/bin/env python

"""
小克(xiaoke)智能体的无障碍服务客户端适配器
支持医疗资源和产品信息的无障碍转换
"""

import asyncio
import logging

# 导入配置
import os
import sys
from typing import Any

import grpc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 实际项目中需要导入生成的proto文件
# from accessibility_service.api.grpc import accessibility_pb2 as pb2
# from accessibility_service.api.grpc import accessibility_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)


class AccessibilityClient:
    """无障碍服务客户端适配器，为小克智能体提供无障碍能力"""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        初始化客户端

        Args:
            config: 配置字典，包含无障碍服务的连接信息
        """
        self.config = config or {}
        self.channel = None
        self.stub = None
        self._connect()
        logger.info("小克智能体无障碍服务客户端初始化完成")

    def _connect(self):
        """连接到无障碍服务"""
        try:
            # 从配置获取服务地址
            host = self.config.get("accessibility_service", {}).get(
                "host", "accessibility-service"
            )
            port = self.config.get("accessibility_service", {}).get("port", 50051)

            # 创建gRPC通道
            self.channel = grpc.insecure_channel(f"{host}:{port}")

            # 导入生成的proto文件（实际项目中需要正确的导入路径）
            # from accessibility_service.api.grpc import accessibility_pb2_grpc as pb2_grpc
            # self.stub = pb2_grpc.AccessibilityServiceStub(self.channel)

            # 模拟stub（实际项目中替换为真实的stub）
            self.stub = MockAccessibilityStub()

            logger.info(f"已连接到无障碍服务: {host}:{port}")

        except Exception as e:
            logger.error(f"连接无障碍服务失败: {e}")
            self.stub = MockAccessibilityStub()  # 使用模拟客户端作为降级

    async def convert_medical_resource_to_accessible(
        self, resource_info: dict[str, Any], user_id: str, target_format: str = "audio"
    ) -> dict[str, Any]:
        """
        将医疗资源信息转换为无障碍格式

        Args:
            resource_info: 医疗资源信息
            user_id: 用户ID
            target_format: 目标格式（audio/simplified/braille）

        Returns:
            无障碍格式的资源信息
        """
        try:
            logger.info(f"转换医疗资源信息: 用户={user_id}, 格式={target_format}")

            # 构建请求
            request = {
                "content_id": f"medical_resource_{resource_info.get('resource_id', 'unknown')}",
                "content_type": "medical_resource",
                "user_id": user_id,
                "target_format": target_format,
                "preferences": {
                    "language": "zh-CN",
                    "voice_type": "professional",
                    "speech_rate": 1.0,
                    "medical_terminology": True,
                },
            }

            # 调用无障碍服务的内容转换接口
            response = await self._call_accessible_content(request)

            # 处理医疗资源特定信息
            accessible_info = self._format_medical_resource_content(
                resource_info, response, target_format
            )

            return {
                "accessible_content": accessible_info,
                "content_url": response.get("content_url", ""),
                "audio_content": response.get("audio_content", b""),
                "tactile_content": response.get("tactile_content", b""),
                "success": True,
            }

        except Exception as e:
            logger.error(f"医疗资源无障碍转换失败: {e}")
            return {
                "accessible_content": f"医疗资源信息转换失败: {e!s}",
                "content_url": "",
                "audio_content": b"",
                "tactile_content": b"",
                "success": False,
                "error": str(e),
            }

    async def convert_product_info_to_accessible(
        self, product_info: dict[str, Any], user_id: str, target_format: str = "audio"
    ) -> dict[str, Any]:
        """
        将农产品信息转换为无障碍格式

        Args:
            product_info: 农产品信息
            user_id: 用户ID
            target_format: 目标格式

        Returns:
            无障碍格式的产品信息
        """
        try:
            logger.info(
                f"转换农产品信息: 用户={user_id}, 产品={product_info.get('name', 'unknown')}"
            )

            # 构建请求
            request = {
                "content_id": f"product_{product_info.get('product_id', 'unknown')}",
                "content_type": "product_info",
                "user_id": user_id,
                "target_format": target_format,
                "preferences": {
                    "language": "zh-CN",
                    "voice_type": "friendly",
                    "speech_rate": 1.0,
                    "include_nutrition": True,
                },
            }

            # 调用无障碍服务的内容转换接口
            response = await self._call_accessible_content(request)

            # 处理农产品特定信息
            accessible_info = self._format_product_content(
                product_info, response, target_format
            )

            return {
                "accessible_content": accessible_info,
                "content_url": response.get("content_url", ""),
                "audio_content": response.get("audio_content", b""),
                "tactile_content": response.get("tactile_content", b""),
                "success": True,
            }

        except Exception as e:
            logger.error(f"农产品信息无障碍转换失败: {e}")
            return {
                "accessible_content": f"农产品信息转换失败: {e!s}",
                "content_url": "",
                "audio_content": b"",
                "tactile_content": b"",
                "success": False,
                "error": str(e),
            }

    async def provide_voice_guidance_for_payment(
        self, payment_info: dict[str, Any], user_id: str, language: str = "zh-CN"
    ) -> dict[str, Any]:
        """
        为支付流程提供语音引导

        Args:
            payment_info: 支付信息
            user_id: 用户ID
            language: 语言代码

        Returns:
            语音引导信息
        """
        try:
            logger.info(
                f"提供支付语音引导: 用户={user_id}, 金额={payment_info.get('amount', 0)}"
            )

            # 构建语音引导内容
            guidance_text = self._generate_payment_guidance_text(payment_info)

            # 构建请求
            request = {
                "audio_data": guidance_text.encode("utf-8"),  # 将文本作为音频数据处理
                "user_id": user_id,
                "context": "payment_guidance",
                "language": language,
                "dialect": "standard",
            }

            # 调用无障碍服务的语音辅助接口
            response = await self._call_voice_assistance(request)

            return {
                "guidance_text": guidance_text,
                "audio_guidance": response.get("response_audio", b""),
                "confidence": response.get("confidence", 0.0),
                "success": True,
            }

        except Exception as e:
            logger.error(f"支付语音引导失败: {e}")
            return {
                "guidance_text": f"支付引导生成失败: {e!s}",
                "audio_guidance": b"",
                "confidence": 0.0,
                "success": False,
                "error": str(e),
            }

    async def convert_subscription_info_to_accessible(
        self,
        subscription_info: dict[str, Any],
        user_id: str,
        target_format: str = "audio",
    ) -> dict[str, Any]:
        """
        将订阅信息转换为无障碍格式

        Args:
            subscription_info: 订阅信息
            user_id: 用户ID
            target_format: 目标格式

        Returns:
            无障碍格式的订阅信息
        """
        try:
            logger.info(
                f"转换订阅信息: 用户={user_id}, 订阅={subscription_info.get('plan_name', 'unknown')}"
            )

            # 构建请求
            request = {
                "content_id": f"subscription_{subscription_info.get('subscription_id', 'unknown')}",
                "content_type": "subscription_info",
                "user_id": user_id,
                "target_format": target_format,
                "preferences": {
                    "language": "zh-CN",
                    "voice_type": "professional",
                    "speech_rate": 1.0,
                    "include_pricing": True,
                },
            }

            # 调用无障碍服务的内容转换接口
            response = await self._call_accessible_content(request)

            # 处理订阅特定信息
            accessible_info = self._format_subscription_content(
                subscription_info, response, target_format
            )

            return {
                "accessible_content": accessible_info,
                "content_url": response.get("content_url", ""),
                "audio_content": response.get("audio_content", b""),
                "tactile_content": response.get("tactile_content", b""),
                "success": True,
            }

        except Exception as e:
            logger.error(f"订阅信息无障碍转换失败: {e}")
            return {
                "accessible_content": f"订阅信息转换失败: {e!s}",
                "content_url": "",
                "audio_content": b"",
                "tactile_content": b"",
                "success": False,
                "error": str(e),
            }

    async def provide_screen_reading_for_interface(
        self, screen_data: bytes, user_id: str, interface_type: str = "resource_list"
    ) -> dict[str, Any]:
        """
        为界面提供屏幕阅读服务

        Args:
            screen_data: 屏幕截图数据
            user_id: 用户ID
            interface_type: 界面类型

        Returns:
            屏幕阅读结果
        """
        try:
            logger.info(f"提供界面屏幕阅读: 用户={user_id}, 类型={interface_type}")

            # 构建请求
            request = {
                "screen_data": screen_data,
                "user_id": user_id,
                "context": f"xiaoke_{interface_type}",
                "preferences": {
                    "language": "zh-CN",
                    "detail_level": "medium",
                    "business_context": True,
                },
            }

            # 调用无障碍服务的屏幕阅读接口
            response = await self._call_screen_reading(request)

            # 处理小克特定的界面元素
            enhanced_elements = self._enhance_ui_elements_for_xiaoke(
                response.get("elements", []), interface_type
            )

            return {
                "screen_description": response.get("screen_description", ""),
                "ui_elements": enhanced_elements,
                "audio_description": response.get("audio_description", b""),
                "navigation_hints": self._generate_navigation_hints(
                    enhanced_elements, interface_type
                ),
                "success": True,
            }

        except Exception as e:
            logger.error(f"界面屏幕阅读失败: {e}")
            return {
                "screen_description": f"界面阅读失败: {e!s}",
                "ui_elements": [],
                "audio_description": b"",
                "navigation_hints": [],
                "success": False,
                "error": str(e),
            }

    async def convert_appointment_info_to_accessible(
        self,
        appointment_info: dict[str, Any],
        user_id: str,
        target_format: str = "audio",
    ) -> dict[str, Any]:
        """
        将预约信息转换为无障碍格式

        Args:
            appointment_info: 预约信息
            user_id: 用户ID
            target_format: 目标格式

        Returns:
            无障碍格式的预约信息
        """
        try:
            logger.info(
                f"转换预约信息: 用户={user_id}, 预约={appointment_info.get('appointment_id', 'unknown')}"
            )

            # 构建请求
            request = {
                "content_id": f"appointment_{appointment_info.get('appointment_id', 'unknown')}",
                "content_type": "appointment_info",
                "user_id": user_id,
                "target_format": target_format,
                "preferences": {
                    "language": "zh-CN",
                    "voice_type": "professional",
                    "speech_rate": 1.0,
                    "include_time_details": True,
                },
            }

            # 调用无障碍服务的内容转换接口
            response = await self._call_accessible_content(request)

            # 处理预约特定信息
            accessible_info = self._format_appointment_content(
                appointment_info, response, target_format
            )

            return {
                "accessible_content": accessible_info,
                "content_url": response.get("content_url", ""),
                "audio_content": response.get("audio_content", b""),
                "tactile_content": response.get("tactile_content", b""),
                "success": True,
            }

        except Exception as e:
            logger.error(f"预约信息无障碍转换失败: {e}")
            return {
                "accessible_content": f"预约信息转换失败: {e!s}",
                "content_url": "",
                "audio_content": b"",
                "tactile_content": b"",
                "success": False,
                "error": str(e),
            }

    def _format_medical_resource_content(
        self,
        resource_info: dict[str, Any],
        response: dict[str, Any],
        target_format: str,
    ) -> str:
        """格式化医疗资源内容"""
        name = resource_info.get("name", "未知资源")
        resource_type = resource_info.get("type", "未知类型")
        location = resource_info.get("location", "未知位置")
        rating = resource_info.get("rating", 0)
        price = resource_info.get("price", 0)

        if target_format == "simplified":
            return f"{name}，{resource_type}，位于{location}，评分{rating}分，价格{price}元"
        elif target_format == "audio":
            return f"医疗资源：{name}。类型：{resource_type}。地址：{location}。用户评分：{rating}分。价格：{price}元。"
        else:
            return response.get("accessible_content", f"医疗资源信息：{name}")

    def _format_product_content(
        self, product_info: dict[str, Any], response: dict[str, Any], target_format: str
    ) -> str:
        """格式化农产品内容"""
        name = product_info.get("name", "未知产品")
        origin = product_info.get("origin", "未知产地")
        price = product_info.get("price", 0)
        constitution_benefit = product_info.get("constitution_benefit", "适合所有体质")

        if target_format == "simplified":
            return f"{name}，产地{origin}，价格{price}元，{constitution_benefit}"
        elif target_format == "audio":
            return f"农产品：{name}。产地：{origin}。价格：{price}元。体质适宜性：{constitution_benefit}。"
        else:
            return response.get("accessible_content", f"农产品信息：{name}")

    def _format_subscription_content(
        self,
        subscription_info: dict[str, Any],
        response: dict[str, Any],
        target_format: str,
    ) -> str:
        """格式化订阅内容"""
        plan_name = subscription_info.get("plan_name", "未知套餐")
        status = subscription_info.get("status", "未知状态")
        amount = subscription_info.get("amount", 0)
        next_billing = subscription_info.get("next_billing_date", "未知")

        if target_format == "simplified":
            return f"{plan_name}，状态{status}，月费{amount}元，下次扣费{next_billing}"
        elif target_format == "audio":
            return f"订阅套餐：{plan_name}。当前状态：{status}。月费：{amount}元。下次扣费日期：{next_billing}。"
        else:
            return response.get("accessible_content", f"订阅信息：{plan_name}")

    def _format_appointment_content(
        self,
        appointment_info: dict[str, Any],
        response: dict[str, Any],
        target_format: str,
    ) -> str:
        """格式化预约内容"""
        doctor_name = appointment_info.get("doctor_name", "未知医生")
        confirmed_time = appointment_info.get("confirmed_time", "未确认时间")
        location = appointment_info.get("location", "未知地点")
        appointment_type = appointment_info.get("appointment_type", "未知类型")

        if target_format == "simplified":
            return f"预约{doctor_name}医生，时间{confirmed_time}，地点{location}"
        elif target_format == "audio":
            return f"预约信息：医生{doctor_name}，预约时间{confirmed_time}，就诊地点{location}，预约类型{appointment_type}。"
        else:
            return response.get("accessible_content", f"预约信息：{doctor_name}")

    def _generate_payment_guidance_text(self, payment_info: dict[str, Any]) -> str:
        """生成支付引导文本"""
        amount = payment_info.get("amount", 0)
        payment_method = payment_info.get("payment_method", "未知支付方式")
        order_id = payment_info.get("order_id", "未知订单")

        return f"您即将支付{amount}元，使用{payment_method}支付方式，订单号{order_id}。请确认支付信息无误后继续。"

    def _enhance_ui_elements_for_xiaoke(
        self, elements: list[dict[str, Any]], interface_type: str
    ) -> list[dict[str, Any]]:
        """为小克界面增强UI元素信息"""
        enhanced_elements = []

        for element in elements:
            enhanced_element = element.copy()

            # 根据界面类型添加特定的上下文信息
            if interface_type == "resource_list":
                if element.get("element_type") == "button" and "预约" in element.get(
                    "content", ""
                ):
                    enhanced_element["accessibility_hint"] = (
                        "点击此按钮可预约该医疗资源"
                    )
                elif element.get("element_type") == "text" and "评分" in element.get(
                    "content", ""
                ):
                    enhanced_element["accessibility_hint"] = (
                        "这是用户对该资源的评分信息"
                    )

            elif interface_type == "product_list":
                if element.get("element_type") == "button" and "购买" in element.get(
                    "content", ""
                ):
                    enhanced_element["accessibility_hint"] = "点击此按钮可购买该农产品"
                elif element.get("element_type") == "text" and "价格" in element.get(
                    "content", ""
                ):
                    enhanced_element["accessibility_hint"] = "这是产品的价格信息"

            elif interface_type == "payment":
                if element.get("element_type") == "button" and "确认" in element.get(
                    "content", ""
                ):
                    enhanced_element["accessibility_hint"] = "点击此按钮确认支付"
                elif element.get("element_type") == "input":
                    enhanced_element["accessibility_hint"] = "请输入支付相关信息"

            enhanced_elements.append(enhanced_element)

        return enhanced_elements

    def _generate_navigation_hints(
        self, elements: list[dict[str, Any]], interface_type: str
    ) -> list[str]:
        """生成导航提示"""
        hints = []

        if interface_type == "resource_list":
            hints.append("使用Tab键在医疗资源列表中导航")
            hints.append("按空格键或回车键选择资源")
            hints.append("按Escape键返回上级菜单")

        elif interface_type == "product_list":
            hints.append("使用方向键浏览农产品列表")
            hints.append("按回车键查看产品详情")
            hints.append("按C键添加到购物车")

        elif interface_type == "payment":
            hints.append("请仔细核对支付信息")
            hints.append("使用Tab键在支付选项间切换")
            hints.append("按回车键确认支付")

        return hints

    # 模拟的服务调用方法（实际项目中替换为真实的gRPC调用）
    async def _call_accessible_content(self, request: dict[str, Any]) -> dict[str, Any]:
        """调用无障碍内容转换服务"""
        await asyncio.sleep(0.1)
        content_type = request.get("content_type", "unknown")

        if content_type == "medical_resource":
            return {
                "accessible_content": "北京协和医院心内科，三甲医院，位于东城区，专业治疗心血管疾病",
                "content_url": "https://accessibility.suoke.life/medical/123",
                "audio_content": b"mock_medical_audio",
                "tactile_content": b"mock_medical_braille",
            }
        elif content_type == "product_info":
            return {
                "accessible_content": "有机红枣，产自新疆和田，富含维生素C，适合气虚体质",
                "content_url": "https://accessibility.suoke.life/product/456",
                "audio_content": b"mock_product_audio",
                "tactile_content": b"mock_product_braille",
            }
        else:
            return {
                "accessible_content": "信息已转换为无障碍格式",
                "content_url": "https://accessibility.suoke.life/content/789",
                "audio_content": b"mock_audio_content",
                "tactile_content": b"mock_braille_content",
            }

    async def _call_voice_assistance(self, request: dict[str, Any]) -> dict[str, Any]:
        """调用语音辅助服务"""
        await asyncio.sleep(0.1)
        return {
            "recognized_text": "支付引导请求",
            "response_text": "支付流程语音引导",
            "response_audio": b"mock_payment_guidance_audio",
            "confidence": 0.95,
        }

    async def _call_screen_reading(self, request: dict[str, Any]) -> dict[str, Any]:
        """调用屏幕阅读服务"""
        await asyncio.sleep(0.1)
        context = request.get("context", "")

        if "resource_list" in context:
            return {
                "screen_description": "当前显示医疗资源列表，包含3个可选项",
                "elements": [
                    {
                        "element_type": "button",
                        "content": "预约北京协和医院",
                        "action": "click",
                        "location": {"x": 100, "y": 100, "width": 200, "height": 50},
                    },
                    {
                        "element_type": "text",
                        "content": "评分：4.8分",
                        "action": "read",
                        "location": {"x": 100, "y": 160, "width": 100, "height": 20},
                    },
                ],
                "audio_description": b"mock_resource_screen_audio",
            }
        elif "product_list" in context:
            return {
                "screen_description": "当前显示农产品列表，包含多个有机产品",
                "elements": [
                    {
                        "element_type": "button",
                        "content": "购买有机红枣",
                        "action": "click",
                        "location": {"x": 100, "y": 100, "width": 150, "height": 40},
                    },
                    {
                        "element_type": "text",
                        "content": "价格：68元/斤",
                        "action": "read",
                        "location": {"x": 100, "y": 150, "width": 100, "height": 20},
                    },
                ],
                "audio_description": b"mock_product_screen_audio",
            }
        else:
            return {
                "screen_description": "当前显示小克服务界面",
                "elements": [],
                "audio_description": b"mock_screen_audio",
            }

    def close(self):
        """关闭客户端连接"""
        if self.channel:
            self.channel.close()
        logger.info("小克无障碍服务客户端连接已关闭")


class MockAccessibilityStub:
    """模拟的无障碍服务存根（用于开发和测试）"""

    def __init__(self):
        logger.info("使用模拟无障碍服务存根")

    async def AccessibleContent(self, request):
        """模拟无障碍内容转换"""
        await asyncio.sleep(0.1)
        return type(
            "Response",
            (),
            {
                "accessible_content": "模拟无障碍内容",
                "content_url": "https://mock.url",
                "audio_content": b"mock_audio",
                "tactile_content": b"mock_braille",
            },
        )()


# 单例实例
accessibility_client = AccessibilityClient()
