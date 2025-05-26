#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小艾智能体设备集成测试
测试摄像头、麦克风、屏幕等设备功能
"""

import asyncio
import logging
import sys
import os
import time
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from internal.integration.device_manager import get_device_manager, DeviceConfig
from internal.integration.accessibility_client import get_accessibility_client, AccessibilityConfig
from internal.agent.agent_manager import AgentManager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

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
            # 初始化设备管理器
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
            
            # 初始化无障碍客户端
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
            
            # 初始化智能体管理器
            self.agent_manager = AgentManager()
            await self.agent_manager.initialize()
            logger.info("✅ 智能体管理器初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 测试环境设置失败: {e}")
            raise
    
    async def test_device_status(self):
        """测试设备状态检查"""
        logger.info("📊 测试设备状态检查...")
        
        try:
            status = await self.device_manager.get_status()
            
            self.test_results['device_status'] = {
                'success': True,
                'data': status,
                'message': '设备状态检查成功'
            }
            
            logger.info(f"✅ 设备状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            self.test_results['device_status'] = {
                'success': False,
                'error': str(e),
                'message': '设备状态检查失败'
            }
            logger.error(f"❌ 设备状态检查失败: {e}")
    
    async def test_camera_capture(self):
        """测试摄像头拍照"""
        logger.info("📷 测试摄像头拍照...")
        
        try:
            result = await self.device_manager.capture_image()
            
            if result['success']:
                image_data = result['data']
                logger.info(f"✅ 拍照成功: {image_data['width']}x{image_data['height']}, "
                          f"大小: {image_data['size_bytes']} bytes")
                
                # 如果有无障碍客户端，测试图像分析
                if self.accessibility_client:
                    try:
                        analysis = await self.accessibility_client.process_image_input(
                            image_data=image_data['image_base64'],
                            user_id="test_user",
                            analysis_type="medical"
                        )
                        logger.info(f"✅ 图像分析成功: {analysis.get('description', '无描述')}")
                        result['accessibility_analysis'] = analysis
                    except Exception as e:
                        logger.warning(f"⚠️ 图像分析失败: {e}")
                
                self.test_results['camera_capture'] = {
                    'success': True,
                    'data': {
                        'width': image_data['width'],
                        'height': image_data['height'],
                        'size_bytes': image_data['size_bytes'],
                        'format': image_data['format']
                    },
                    'message': '摄像头拍照成功'
                }
            else:
                raise Exception(result.get('error', '拍照失败'))
                
        except Exception as e:
            self.test_results['camera_capture'] = {
                'success': False,
                'error': str(e),
                'message': '摄像头拍照失败'
            }
            logger.error(f"❌ 摄像头拍照失败: {e}")
    
    async def test_microphone_recording(self):
        """测试麦克风录音"""
        logger.info("🎤 测试麦克风录音...")
        
        try:
            logger.info("开始录音（3秒）...")
            result = await self.device_manager.record_audio(duration=3.0)
            
            if result['success']:
                audio_data = result['data']
                logger.info(f"✅ 录音成功: 时长 {audio_data['duration']}s, "
                          f"大小: {audio_data['size_bytes']} bytes")
                
                # 如果有无障碍客户端，测试语音识别
                if self.accessibility_client:
                    try:
                        recognition = await self.accessibility_client.process_voice_input(
                            audio_data=audio_data['audio_base64'],
                            user_id="test_user",
                            language="zh-CN"
                        )
                        logger.info(f"✅ 语音识别成功: {recognition.get('text', '无识别结果')}")
                        result['accessibility_recognition'] = recognition
                    except Exception as e:
                        logger.warning(f"⚠️ 语音识别失败: {e}")
                
                self.test_results['microphone_recording'] = {
                    'success': True,
                    'data': {
                        'duration': audio_data['duration'],
                        'size_bytes': audio_data['size_bytes'],
                        'sample_rate': audio_data['sample_rate'],
                        'channels': audio_data['channels']
                    },
                    'message': '麦克风录音成功'
                }
            else:
                raise Exception(result.get('error', '录音失败'))
                
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
            result = await self.device_manager.capture_screen()
            
            if result['success']:
                screen_data = result['data']
                logger.info(f"✅ 截图成功: {screen_data['width']}x{screen_data['height']}, "
                          f"大小: {screen_data['size_bytes']} bytes")
                
                # 如果有无障碍客户端，测试屏幕阅读
                if self.accessibility_client:
                    try:
                        reading = await self.accessibility_client.provide_screen_reading(
                            screen_data=screen_data['image_base64'],
                            user_id="test_user",
                            reading_mode="detailed"
                        )
                        logger.info(f"✅ 屏幕阅读成功: {reading.get('description', '无描述')}")
                        result['accessibility_reading'] = reading
                    except Exception as e:
                        logger.warning(f"⚠️ 屏幕阅读失败: {e}")
                
                self.test_results['screen_capture'] = {
                    'success': True,
                    'data': {
                        'width': screen_data['width'],
                        'height': screen_data['height'],
                        'size_bytes': screen_data['size_bytes'],
                        'format': screen_data['format']
                    },
                    'message': '屏幕截图成功'
                }
            else:
                raise Exception(result.get('error', '截图失败'))
                
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
            logger.warning("⚠️ 无障碍客户端不可用，跳过测试")
            return
        
        try:
            # 测试内容生成
            content_result = await self.accessibility_client.generate_accessible_content(
                content="这是一个健康建议：多喝水，适量运动",
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
        # 设置测试环境
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