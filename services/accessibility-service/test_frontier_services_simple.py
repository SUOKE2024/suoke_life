#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索克生活 - 前沿技术服务简化测试
验证BCI、触觉反馈和空间音频服务的基本功能
"""

import asyncio
import time

# 导入服务实现
from internal.service.implementations.bci_impl import BCIServiceImpl
from internal.service.implementations.haptic_feedback_impl import HapticFeedbackServiceImpl
from internal.service.implementations.spatial_audio_impl import SpatialAudioServiceImpl

# 导入接口和枚举
from internal.service.interfaces.bci_interface import BCIDeviceType, SignalType, BCICommand
from internal.service.interfaces.haptic_feedback_interface import HapticDeviceType, HapticPattern, HapticIntensity
from internal.service.interfaces.spatial_audio_interface import AudioRenderingEngine


async def test_bci_service():
    """测试BCI服务基本功能"""
    print("🧠 测试BCI服务...")
    
    bci_service = BCIServiceImpl()
    try:
        await bci_service.initialize()
        
        # 基本功能测试
        devices = await bci_service.detect_bci_devices()
        connect_result = await bci_service.connect_bci_device("test_device", BCIDeviceType.EEG)
        
        signal_data = {"data": [[1, 2], [3, 4]], "channels": ["C3", "C4"]}
        process_result = await bci_service.process_brain_signals("test_user", "test_device", signal_data)
        
        print(f"✅ BCI服务测试通过")
        return True
        
    except Exception as e:
        print(f"❌ BCI服务测试失败: {e}")
        return False
    finally:
        await bci_service.cleanup()


async def test_haptic_service():
    """测试触觉反馈服务基本功能"""
    print("🤲 测试触觉反馈服务...")
    
    haptic_service = HapticFeedbackServiceImpl()
    try:
        await haptic_service.initialize()
        
        # 基本功能测试
        devices = await haptic_service.detect_haptic_devices()
        connect_result = await haptic_service.connect_haptic_device("test_device", HapticDeviceType.HAPTIC_GLOVES)
        
        # 修复：使用正确的方法签名
        pattern_result = await haptic_service.create_haptic_pattern("test_pattern", {
            "type": HapticPattern.PULSE.value,
            "intensity": HapticIntensity.MEDIUM.value
        })
        
        play_result = await haptic_service.play_haptic_pattern("test_user", "test_device", "test_pattern")
        
        print(f"✅ 触觉反馈服务测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 触觉反馈服务测试失败: {e}")
        return False
    finally:
        await haptic_service.cleanup()


async def test_spatial_audio_service():
    """测试空间音频服务基本功能"""
    print("🔊 测试空间音频服务...")
    
    audio_service = SpatialAudioServiceImpl()
    try:
        await audio_service.initialize()
        
        # 基本功能测试
        devices = await audio_service.detect_audio_devices()
        config_result = await audio_service.configure_audio_device("test_device", {"channels": 2})
        
        scene_result = await audio_service.create_spatial_scene("test_user", "test_scene", {})
        
        # 修复：使用正确的方法签名
        source_result = await audio_service.add_audio_source("test_user", "test_scene", {
            "source_name": "test_source",
            "position": [0, 0, 0]
        })
        
        render_result = await audio_service.render_spatial_audio("test_user", "test_scene", {})
        
        print(f"✅ 空间音频服务测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 空间音频服务测试失败: {e}")
        return False
    finally:
        await audio_service.cleanup()


async def test_service_integration():
    """测试服务集成"""
    print("🔗 测试服务集成...")
    
    try:
        # 初始化所有服务
        bci_service = BCIServiceImpl()
        haptic_service = HapticFeedbackServiceImpl()
        audio_service = SpatialAudioServiceImpl()
        
        await bci_service.initialize()
        await haptic_service.initialize()
        await audio_service.initialize()
        
        # 简单集成测试
        await bci_service.connect_bci_device("bci_device", BCIDeviceType.EEG)
        await haptic_service.connect_haptic_device("haptic_device", HapticDeviceType.HAPTIC_VEST)
        await audio_service.configure_audio_device("audio_device", {"channels": 2})
        
        print(f"✅ 服务集成测试通过")
        
        # 清理资源
        await bci_service.cleanup()
        await haptic_service.cleanup()
        await audio_service.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ 服务集成测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 索克生活 - 前沿技术服务简化测试")
    print("=" * 60)
    
    start_time = time.time()
    
    # 运行测试
    tests = [
        test_bci_service(),
        test_haptic_service(), 
        test_spatial_audio_service(),
        test_service_integration()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    # 统计结果
    passed = sum(1 for result in results if result is True)
    total = len(results)
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果:")
    print(f"   • 通过: {passed}/{total}")
    print(f"   • 成功率: {passed/total*100:.1f}%")
    print(f"   • 耗时: {elapsed_time:.2f}s")
    
    if passed == total:
        print(f"\n🎉 所有前沿技术服务测试通过！")
    else:
        print(f"\n⚠️  部分测试失败，请检查相关服务")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main()) 