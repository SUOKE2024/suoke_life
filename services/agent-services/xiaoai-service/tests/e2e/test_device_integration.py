"""
test_device_integration - 索克生活项目模块
"""

from internal.integration.accessibility_client import (
from internal.integration.device_manager import DeviceConfig, get_device_manager
from pathlib import Path
import asyncio
import logging
import sys

#!/usr/bin/env python3
"""
小艾智能体设备集成测试
测试摄像头、麦克风、屏幕等设备功能
"""


# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

    AccessibilityConfig,
    get_accessibility_client,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
# 使用loguru logger

class DeviceIntegrationTester:
    """设备集成测试器"""

    def __init__(self):
        self.device_manager = None
        self.accessibility_client = None
        self.agent_manager = None
        self.test_results = {}

    async def setup(self):
        """设置测试环境"""
        logger.info("🔧 设置测试环境...")

        try:
            device_config = DeviceConfig(
                camera_enabled=True,
                microphone_enabled=True,
                screen_enabled=True,
                camera_index=0,
                camera_width=640,
                camera_height=480,
                sample_rate=16000,
                channels=1,
                chunk_size=1024,
                max_recording_duration=5.0,
                max_image_size=1048576,
                check_permissions=False,  # 测试时跳过权限检查
                init_timeout=10
            )

            self.device_manager = await get_device_manager(device_config)
            logger.info("✅ 设备管理器初始化成功")

            accessibility_config = AccessibilityConfig(
                enabled=True,
                service_url="http://localhost:50051",
                voice_assistance=True,
                image_assistance=True,
                screen_reading=True,
                content_generation=True,
                timeout=10.0,
                retry_attempts=2
            )

            try:
                self.accessibility_client = await get_accessibility_client(accessibility_config)
                logger.info("✅ 无障碍客户端初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ 无障碍客户端初始化失败: {e}")
                self.accessibility_client = None

        except Exception as e:
            logger.error(f"❌ 设备管理器初始化失败: {e}")
            raise

    async def test_device_status(self):
        """测试设备状态"""
        logger.info("📱 测试设备状态...")

        try:
            if self.device_manager:
                status = await self.device_manager.get_device_status()
                self.test_results['device_status'] = {
                    'success': True,
                    'data': status,
                    'message': '设备状态获取成功'
                }
                logger.info("✅ 设备状态获取成功")
            else:
                raise Exception("设备管理器不可用")

        except Exception as e:
            self.test_results['device_status'] = {
                'success': False,
                'error': str(e),
                'message': '设备状态获取失败'
            }
            logger.error(f"❌ 设备状态获取失败: {e}")

    async def test_camera_capture(self):
        """测试摄像头拍摄"""
        logger.info("📷 测试摄像头拍摄...")

        try:
            if self.device_manager:
                result = await self.device_manager.capture_camera_image(
                    quality="medium",
                    format="jpeg"
                )

                if result['success']:
                    self.test_results['camera_capture'] = {
                        'success': True,
                        'data': {
                            'image_size': len(result.get('image_data', b'')),
                            'format': result.get('format', 'unknown')
                        },
                        'message': '摄像头拍摄成功'
                    }
                    logger.info("✅ 摄像头拍摄成功")
                else:
                    raise Exception(result.get('error', '摄像头拍摄失败'))
            else:
                raise Exception("设备管理器不可用")

        except Exception as e:
            self.test_results['camera_capture'] = {
                'success': False,
                'error': str(e),
                'message': '摄像头拍摄失败'
            }
            logger.error(f"❌ 摄像头拍摄失败: {e}")

    async def test_microphone_recording(self):
        """测试麦克风录音"""
        logger.info("🎤 测试麦克风录音...")

        try:
            if self.device_manager:
                result = await self.device_manager.record_microphone_audio(
                    duration=2.0,
                    sample_rate=44100,
                    format="wav"
                )

                if result['success']:
                    self.test_results['microphone_recording'] = {
                        'success': True,
                        'data': {
                            'audio_size': len(result.get('audio_data', b'')),
                            'duration': result.get('duration', 0),
                            'format': result.get('format', 'unknown')
                        },
                        'message': '麦克风录音成功'
                    }
                    logger.info("✅ 麦克风录音成功")
                else:
                    raise Exception(result.get('error', '麦克风录音失败'))
            else:
                raise Exception("设备管理器不可用")

        except Exception as e:
            self.test_results['microphone_recording'] = {
                'success': False,
                'error': str(e),
                'message': '麦克风录音失败'
            }
            logger.error(f"❌ 麦克风录音失败: {e}")

    async def test_screen_capture(self):
        """测试屏幕截图"""
        logger.info("🖥️ 测试屏幕截图...")

        try:
            if self.device_manager:
                result = await self.device_manager.capture_screen_image(
                    quality="medium",
                    format="png"
                )

                if result['success']:
                    self.test_results['screen_capture'] = {
                        'success': True,
                        'data': {
                            'image_size': len(result.get('image_data', b'')),
                            'format': result.get('format', 'unknown')
                        },
                        'message': '屏幕截图成功'
                    }
                    logger.info("✅ 屏幕截图成功")
                else:
                    raise Exception(result.get('error', '屏幕截图失败'))
            else:
                raise Exception("设备管理器不可用")

        except Exception as e:
            self.test_results['screen_capture'] = {
                'success': False,
                'error': str(e),
                'message': '屏幕截图失败'
            }
            logger.error(f"❌ 屏幕截图失败: {e}")

    async def test_agent_integration(self):
        """测试智能体集成"""
        logger.info("🤖 测试智能体集成...")

        try:
            # 测试摄像头集成
            camera_result = await self.agent_manager.capture_camera_image(
                user_id="test_user",
                session_id="test_session"
            )

            if camera_result['success']:
                logger.info("✅ 智能体摄像头集成成功")
            else:
                logger.warning(f"⚠️ 智能体摄像头集成失败: {camera_result.get('error')}")

            # 测试麦克风集成
            mic_result = await self.agent_manager.record_microphone_audio(
                user_id="test_user",
                duration=2.0,
                session_id="test_session"
            )

            if mic_result['success']:
                logger.info("✅ 智能体麦克风集成成功")
            else:
                logger.warning(f"⚠️ 智能体麦克风集成失败: {mic_result.get('error')}")

            # 测试屏幕集成
            screen_result = await self.agent_manager.capture_screen_image(
                user_id="test_user",
                session_id="test_session"
            )

            if screen_result['success']:
                logger.info("✅ 智能体屏幕集成成功")
            else:
                logger.warning(f"⚠️ 智能体屏幕集成失败: {screen_result.get('error')}")

            self.test_results['agent_integration'] = {
                'success': True,
                'data': {
                    'camera': camera_result['success'],
                    'microphone': mic_result['success'],
                    'screen': screen_result['success']
                },
                'message': '智能体集成测试完成'
            }

        except Exception as e:
            self.test_results['agent_integration'] = {
                'success': False,
                'error': str(e),
                'message': '智能体集成测试失败'
            }
            logger.error(f"❌ 智能体集成测试失败: {e}")

    async def test_accessibility_integration(self):
        """测试无障碍集成"""
        logger.info("♿ 测试无障碍集成...")

        if not self.accessibility_client:
            self.test_results['accessibility_integration'] = {
                'success': False,
                'error': '无障碍客户端不可用',
                'message': '无障碍集成测试跳过'
            }
            logger.warning("⚠️ 无障碍客户端不可用,跳过测试")
            return

        try:
            content_result = await self.accessibility_client.generate_accessible_content(
                content="这是一个健康建议:多喝水,适量运动",
                user_id="test_user",
                content_type="health_advice",
                target_format="audio"
            )

            if content_result.get('success'):
                logger.info("✅ 无障碍内容生成成功")
            else:
                logger.warning(f"⚠️ 无障碍内容生成失败: {content_result.get('error')}")

            self.test_results['accessibility_integration'] = {
                'success': True,
                'data': {
                    'content_generation': content_result.get('success', False)
                },
                'message': '无障碍集成测试完成'
            }

        except Exception as e:
            self.test_results['accessibility_integration'] = {
                'success': False,
                'error': str(e),
                'message': '无障碍集成测试失败'
            }
            logger.error(f"❌ 无障碍集成测试失败: {e}")

    async def cleanup(self):
        """清理测试环境"""
        logger.info("🧹 清理测试环境...")

        try:
            if self.device_manager:
                await self.device_manager.close()
                logger.info("✅ 设备管理器已关闭")

            if self.accessibility_client:
                await self.accessibility_client.close()
                logger.info("✅ 无障碍客户端已关闭")

            if self.agent_manager:
                await self.agent_manager.close()
                logger.info("✅ 智能体管理器已关闭")

        except Exception as e:
            logger.error(f"❌ 清理失败: {e}")

    def print_test_summary(self):
        """打印测试总结"""
        logger.info("📋 测试总结")
        logger.info("=" * 60)

        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result['success'])

        logger.info(f"总测试数: {total_tests}")
        logger.info(f"成功测试: {successful_tests}")
        logger.info(f"失败测试: {total_tests - successful_tests}")
        logger.info(f"成功率: {(successful_tests / total_tests * 100):.1f}%")
        logger.info("-" * 60)

        for test_name, result in self.test_results.items():
            status = "✅ 成功" if result['success'] else "❌ 失败"
            logger.info(f"{test_name}: {status} - {result['message']}")
            if not result['success'] and 'error' in result:
                logger.info(f"  错误: {result['error']}")

        logger.info("=" * 60)

async def main():
    """主测试函数"""
    logger.info("🚀 开始小艾智能体设备集成测试")

    tester = DeviceIntegrationTester()

    try:
        await tester.setup()

        # 运行测试
        await tester.test_device_status()
        await tester.test_camera_capture()
        await tester.test_microphone_recording()
        await tester.test_screen_capture()
        await tester.test_agent_integration()
        await tester.test_accessibility_integration()

    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {e}")

    finally:
        # 清理环境
        await tester.cleanup()

        # 打印总结
        tester.print_test_summary()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())
