#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小艾服务无障碍功能集成评估测试
评估小艾服务如何使用无障碍服务能力
"""

import asyncio
import logging
import sys
import os
import time
from typing import Dict, Any, List
import json

# 添加项目路径
sys.path.insert(0, os.path.abspath('.'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AccessibilityIntegrationEvaluator:
    """无障碍功能集成评估器"""
    
    def __init__(self):
        self.evaluation_results = {}
        self.test_user_id = "test_user_accessibility_001"
        
    async def evaluate_accessibility_integration(self) -> Dict[str, Any]:
        """评估无障碍功能集成"""
        logger.info("开始评估小艾服务无障碍功能集成")
        
        evaluation_results = {
            "timestamp": time.time(),
            "service_name": "xiaoai-service",
            "evaluation_type": "accessibility_integration",
            "tests": {}
        }
        
        # 1. 评估无障碍客户端配置
        config_result = await self._evaluate_accessibility_config()
        evaluation_results["tests"]["accessibility_config"] = config_result
        
        # 2. 评估无障碍客户端初始化
        client_result = await self._evaluate_accessibility_client()
        evaluation_results["tests"]["accessibility_client"] = client_result
        
        # 3. 评估语音输入处理能力
        voice_result = await self._evaluate_voice_processing()
        evaluation_results["tests"]["voice_processing"] = voice_result
        
        # 4. 评估图像输入处理能力
        image_result = await self._evaluate_image_processing()
        evaluation_results["tests"]["image_processing"] = image_result
        
        # 5. 评估内容生成能力
        content_result = await self._evaluate_content_generation()
        evaluation_results["tests"]["content_generation"] = content_result
        
        # 6. 评估屏幕阅读能力
        screen_result = await self._evaluate_screen_reading()
        evaluation_results["tests"]["screen_reading"] = screen_result
        
        # 7. 评估服务集成架构
        architecture_result = await self._evaluate_integration_architecture()
        evaluation_results["tests"]["integration_architecture"] = architecture_result
        
        # 8. 评估API接口覆盖
        api_result = await self._evaluate_api_coverage()
        evaluation_results["tests"]["api_coverage"] = api_result
        
        # 计算总体评分
        evaluation_results["overall_score"] = self._calculate_overall_score(evaluation_results["tests"])
        evaluation_results["recommendations"] = self._generate_recommendations(evaluation_results["tests"])
        
        return evaluation_results
    
    async def _evaluate_accessibility_config(self) -> Dict[str, Any]:
        """评估无障碍配置"""
        logger.info("评估无障碍配置...")
        
        try:
            # 检查配置文件
            config_file = "config/accessibility.yaml"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    import yaml
                    config = yaml.safe_load(f)
                
                # 检查配置完整性
                required_sections = ['features', 'defaults', 'health_check', 'logging']
                accessibility_config = config.get('accessibility', {})
                missing_sections = [s for s in required_sections if s not in accessibility_config]
                
                features = config.get('accessibility', {}).get('features', {})
                enabled_features = [k for k, v in features.items() if v]
                
                return {
                    "status": "success",
                    "config_file_exists": True,
                    "missing_sections": missing_sections,
                    "enabled_features": enabled_features,
                    "total_features": len(features),
                    "score": 0.9 if not missing_sections else 0.6
                }
            else:
                return {
                    "status": "warning",
                    "config_file_exists": False,
                    "error": "配置文件不存在",
                    "score": 0.3
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "score": 0.0
            }
    
    async def _evaluate_accessibility_client(self) -> Dict[str, Any]:
        """评估无障碍客户端"""
        logger.info("评估无障碍客户端...")
        
        try:
            # 尝试导入无障碍客户端
            from xiaoai.integration.accessibility_client import AccessibilityServiceClient, AccessibilityConfig
            
            # 创建客户端实例
            config = AccessibilityConfig(enabled=False)  # 测试模式，不连接真实服务
            client = AccessibilityServiceClient(config)
            
            # 检查客户端方法
            methods = [
                'initialize', 'close', 'health_check',
                'process_voice_input', 'process_image_input',
                'generate_accessible_content', 'provide_screen_reading',
                'manage_accessibility_settings', 'translate_speech'
            ]
            
            available_methods = [m for m in methods if hasattr(client, m)]
            
            return {
                "status": "success",
                "client_importable": True,
                "available_methods": available_methods,
                "total_methods": len(methods),
                "method_coverage": len(available_methods) / len(methods),
                "score": len(available_methods) / len(methods)
            }
            
        except ImportError as e:
            return {
                "status": "error",
                "client_importable": False,
                "error": f"导入失败: {str(e)}",
                "score": 0.0
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "score": 0.0
            }
    
    async def _evaluate_voice_processing(self) -> Dict[str, Any]:
        """评估语音处理能力"""
        logger.info("评估语音处理能力...")
        
        try:
            # 检查语音处理相关代码
            from xiaoai.service.xiaoai_service_impl import XiaoaiServiceImpl
            
            service = XiaoaiServiceImpl()
            
            # 检查语音处理方法
            voice_methods = [
                'provide_voice_interaction_accessible',
                'process_multimodal_input_accessible'
            ]
            
            available_voice_methods = [m for m in voice_methods if hasattr(service, m)]
            
            # 模拟语音处理测试
            test_audio_data = b"fake_audio_data"
            
            # 注意：这里只是检查方法存在性，不实际调用
            voice_integration_score = len(available_voice_methods) / len(voice_methods)
            
            return {
                "status": "success",
                "available_voice_methods": available_voice_methods,
                "total_voice_methods": len(voice_methods),
                "voice_integration_score": voice_integration_score,
                "supports_multimodal": hasattr(service, 'process_multimodal_input_accessible'),
                "score": voice_integration_score
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "score": 0.0
            }
    
    async def _evaluate_image_processing(self) -> Dict[str, Any]:
        """评估图像处理能力"""
        logger.info("评估图像处理能力...")
        
        try:
            # 检查图像处理集成
            from xiaoai.agent.agent_manager import AgentManager
            
            manager = AgentManager()
            
            # 检查图像相关方法
            image_methods = [
                'capture_camera_image',
                'capture_screen_image',
                'process_multimodal_input'
            ]
            
            available_image_methods = [m for m in image_methods if hasattr(manager, m)]
            
            image_integration_score = len(available_image_methods) / len(image_methods)
            
            return {
                "status": "success",
                "available_image_methods": available_image_methods,
                "total_image_methods": len(image_methods),
                "image_integration_score": image_integration_score,
                "supports_camera": hasattr(manager, 'capture_camera_image'),
                "supports_screen_capture": hasattr(manager, 'capture_screen_image'),
                "score": image_integration_score
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "score": 0.0
            }
    
    async def _evaluate_content_generation(self) -> Dict[str, Any]:
        """评估内容生成能力"""
        logger.info("评估内容生成能力...")
        
        try:
            from xiaoai.agent.agent_manager import AgentManager
            
            manager = AgentManager()
            
            # 检查内容生成方法
            content_methods = [
                'generate_accessible_content',
                'generate_health_summary'
            ]
            
            available_content_methods = [m for m in content_methods if hasattr(manager, m)]
            
            content_integration_score = len(available_content_methods) / len(content_methods)
            
            return {
                "status": "success",
                "available_content_methods": available_content_methods,
                "total_content_methods": len(content_methods),
                "content_integration_score": content_integration_score,
                "supports_accessible_generation": hasattr(manager, 'generate_accessible_content'),
                "score": content_integration_score
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "score": 0.0
            }
    
    async def _evaluate_screen_reading(self) -> Dict[str, Any]:
        """评估屏幕阅读能力"""
        logger.info("评估屏幕阅读能力...")
        
        try:
            # 检查屏幕阅读相关代码
            from xiaoai.integration.accessibility_client import AccessibilityServiceClient
            
            client = AccessibilityServiceClient()
            
            # 检查屏幕阅读方法
            screen_methods = ['provide_screen_reading']
            available_screen_methods = [m for m in screen_methods if hasattr(client, m)]
            
            screen_integration_score = len(available_screen_methods) / len(screen_methods)
            
            return {
                "status": "success",
                "available_screen_methods": available_screen_methods,
                "total_screen_methods": len(screen_methods),
                "screen_integration_score": screen_integration_score,
                "supports_screen_reading": len(available_screen_methods) > 0,
                "score": screen_integration_score
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "score": 0.0
            }
    
    async def _evaluate_integration_architecture(self) -> Dict[str, Any]:
        """评估集成架构"""
        logger.info("评估集成架构...")
        
        try:
            # 检查架构组件
            architecture_components = {
                "accessibility_client": "xiaoai/integration/accessibility_client.py",
                "service_impl": "xiaoai/service/xiaoai_service_impl.py",
                "agent_manager": "xiaoai/agent/agent_manager.py",
                "device_handler": "xiaoai/delivery/api/device_handler.py",
                "config_file": "config/accessibility.yaml"
            }
            
            existing_components = {}
            for name, path in architecture_components.items():
                existing_components[name] = os.path.exists(path)
            
            architecture_score = sum(existing_components.values()) / len(existing_components)
            
            return {
                "status": "success",
                "architecture_components": existing_components,
                "total_components": len(architecture_components),
                "architecture_completeness": architecture_score,
                "missing_components": [k for k, v in existing_components.items() if not v],
                "score": architecture_score
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "score": 0.0
            }
    
    async def _evaluate_api_coverage(self) -> Dict[str, Any]:
        """评估API覆盖率"""
        logger.info("评估API覆盖率...")
        
        try:
            # 检查无障碍服务API覆盖
            from xiaoai.integration.accessibility_client import AccessibilityServiceClient
            
            client = AccessibilityServiceClient()
            
            # 无障碍服务的主要API
            expected_apis = [
                'process_voice_input',           # 语音辅助
                'process_image_input',           # 图像辅助  
                'provide_screen_reading',        # 屏幕阅读
                'generate_accessible_content',   # 内容转换
                'manage_accessibility_settings', # 设置管理
                'translate_speech'               # 语音翻译
            ]
            
            implemented_apis = [api for api in expected_apis if hasattr(client, api)]
            api_coverage = len(implemented_apis) / len(expected_apis)
            
            return {
                "status": "success",
                "expected_apis": expected_apis,
                "implemented_apis": implemented_apis,
                "missing_apis": [api for api in expected_apis if api not in implemented_apis],
                "api_coverage": api_coverage,
                "score": api_coverage
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "score": 0.0
            }
    
    def _calculate_overall_score(self, tests: Dict[str, Any]) -> float:
        """计算总体评分"""
        scores = [test.get("score", 0.0) for test in tests.values()]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _generate_recommendations(self, tests: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于测试结果生成建议
        for test_name, test_result in tests.items():
            score = test_result.get("score", 0.0)
            
            if score < 0.5:
                if test_name == "accessibility_config":
                    recommendations.append("完善无障碍服务配置文件，确保所有必要配置项都已设置")
                elif test_name == "accessibility_client":
                    recommendations.append("修复无障碍客户端导入问题，确保所有方法都可用")
                elif test_name == "voice_processing":
                    recommendations.append("增强语音处理能力，实现更完整的语音交互功能")
                elif test_name == "image_processing":
                    recommendations.append("完善图像处理集成，支持更多图像输入场景")
                elif test_name == "content_generation":
                    recommendations.append("扩展内容生成能力，支持更多无障碍格式")
                elif test_name == "screen_reading":
                    recommendations.append("实现屏幕阅读功能，提升界面无障碍体验")
                elif test_name == "integration_architecture":
                    recommendations.append("完善集成架构，确保所有组件都正确配置")
                elif test_name == "api_coverage":
                    recommendations.append("实现缺失的无障碍API，提高功能覆盖率")
            elif score < 0.8:
                recommendations.append(f"优化{test_name}功能，提升性能和稳定性")
        
        if not recommendations:
            recommendations.append("无障碍功能集成良好，建议继续优化用户体验")
        
        return recommendations

async def main():
    """主函数"""
    evaluator = AccessibilityIntegrationEvaluator()
    
    try:
        # 执行评估
        results = await evaluator.evaluate_accessibility_integration()
        
        # 输出结果
        print("\n" + "="*80)
        print("小艾服务无障碍功能集成评估报告")
        print("="*80)
        
        print(f"\n📊 总体评分: {results['overall_score']:.2f}/1.00")
        
        print(f"\n🔍 详细测试结果:")
        for test_name, test_result in results["tests"].items():
            status = test_result.get("status", "unknown")
            score = test_result.get("score", 0.0)
            
            status_emoji = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
            print(f"  {status_emoji} {test_name}: {score:.2f} ({status})")
            
            if "error" in test_result:
                print(f"    错误: {test_result['error']}")
        
        print(f"\n💡 改进建议:")
        for i, recommendation in enumerate(results["recommendations"], 1):
            print(f"  {i}. {recommendation}")
        
        # 保存详细结果到文件
        with open("accessibility_integration_evaluation_report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存到: accessibility_integration_evaluation_report.json")
        
        return results
        
    except Exception as e:
        logger.error(f"评估过程中发生错误: {e}")
        return {"error": str(e), "overall_score": 0.0}

if __name__ == "__main__":
    asyncio.run(main()) 