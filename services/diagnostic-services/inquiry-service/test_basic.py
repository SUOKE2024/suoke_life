#!/usr/bin/env python
"""
基本功能测试脚本
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_basic_imports():
    """测试基本模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from proto import inquiry_service_pb2, inquiry_service_pb2_grpc
        print("✅ Proto 模块导入成功")
    except Exception as e:
        print(f"❌ Proto 模块导入失败: {e}")
        return False
    
    try:
        from internal.dialogue.dialogue_manager import DialogueManager
        print("✅ DialogueManager 导入成功")
    except Exception as e:
        print(f"❌ DialogueManager 导入失败: {e}")
        return False
    
    try:
        from internal.symptom.optimized_symptom_extractor import OptimizedSymptomExtractor
        print("✅ OptimizedSymptomExtractor 导入成功")
    except Exception as e:
        print(f"❌ OptimizedSymptomExtractor 导入失败: {e}")
        return False
    
    try:
        from internal.tcm.pattern_mapper import TCMPatternMapper
        print("✅ TCMPatternMapper 导入成功")
    except Exception as e:
        print(f"❌ TCMPatternMapper 导入失败: {e}")
        return False
    
    return True

async def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        # 测试配置
        config = {
            "llm": {
                "model": "test-model",
                "use_mock_mode": True,
                "temperature": 0.7,
            },
            "dialogue": {
                "max_session_duration": 3600,
                "session_timeout": 1800,
            },
            "symptom_extraction": {
                "confidence_threshold": 0.6,
                "max_symptoms_per_text": 10,
            },
            "tcm_mapping": {
                "confidence_threshold": 0.6,
                "max_patterns_per_analysis": 5,
            },
        }
        
        # 测试症状提取器
        from internal.symptom.optimized_symptom_extractor import OptimizedSymptomExtractor
        extractor = OptimizedSymptomExtractor(config)
        print("✅ 症状提取器初始化成功")
        
        # 测试中医证型映射器
        from internal.tcm.pattern_mapper import TCMPatternMapper
        mapper = TCMPatternMapper(config)
        print("✅ 中医证型映射器初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

async def test_grpc_service():
    """测试gRPC服务"""
    print("\n🌐 测试gRPC服务...")
    
    try:
        from api.grpc.inquiry_service import InquiryServiceServicer
        from proto import inquiry_service_pb2_grpc
        
        # 创建服务实例
        config = {
            "llm": {"use_mock_mode": True},
            "dialogue": {"max_session_duration": 3600},
            "symptom_extraction": {"confidence_threshold": 0.6},
            "tcm_mapping": {"confidence_threshold": 0.6},
        }
        
        servicer = InquiryServiceServicer(config)
        print("✅ gRPC服务初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ gRPC服务测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始 inquiry-service 基本功能测试\n")
    
    # 测试模块导入
    import_success = await test_basic_imports()
    
    # 测试基本功能
    if import_success:
        func_success = await test_basic_functionality()
        
        # 测试gRPC服务
        if func_success:
            grpc_success = await test_grpc_service()
            
            if grpc_success:
                print("\n🎉 所有基本测试通过！")
                print("\n📊 测试总结:")
                print("✅ 模块导入: 通过")
                print("✅ 基本功能: 通过") 
                print("✅ gRPC服务: 通过")
                print("\n🔧 inquiry-service 已达到基本可用状态")
                return True
    
    print("\n❌ 测试失败，请检查错误信息")
    return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 