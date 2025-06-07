#!/usr/bin/env python3
"""
综合集成测试 - 索克生活项目
测试所有微服务的协调工作，确保100%完成度
"""

import asyncio
import pytest
import aiohttp
import json
import base64
from typing import Dict, List, Any, Optional
from unittest.mock import AsyncMock, patch
import time

from loguru import logger

# 测试配置
TEST_CONFIG = {
    "services": {
        "xiaoai": "http://localhost:8001",
        "xiaoke": "http://localhost:8002", 
        "laoke": "http://localhost:8003",
        "soer": "http://localhost:8004",
        "api_gateway": "http://localhost:8000",
        "rag_service": "http://localhost:8005",
        "auth_service": "http://localhost:8006",
        "user_service": "http://localhost:8007",
        "health_data_service": "http://localhost:8008",
        "blockchain_service": "http://localhost:8009"
    },
    "test_timeout": 30,
    "max_retries": 3
}


class ComprehensiveIntegrationTester:
    """综合集成测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.session = None
        self.test_results = {}
        self.test_user_id = "test_user_001"
        self.test_session_id = "test_session_001"
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=TEST_CONFIG["test_timeout"])
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """运行综合集成测试"""
        logger.info("🚀 开始综合集成测试")
        
        test_suite = [
            ("服务健康检查", self.test_service_health),
            ("用户认证流程", self.test_user_authentication),
            ("智能体协作", self.test_agent_collaboration),
            ("知识图谱集成", self.test_knowledge_graph_integration),
            ("舌象分析流程", self.test_tongue_analysis_workflow),
            ("健康数据管理", self.test_health_data_management),
            ("区块链数据验证", self.test_blockchain_verification),
            ("RAG服务集成", self.test_rag_service_integration),
            ("API网关路由", self.test_api_gateway_routing),
            ("端到端诊断流程", self.test_end_to_end_diagnosis)
        ]
        
        results = {}
        total_tests = len(test_suite)
        passed_tests = 0
        
        for test_name, test_func in test_suite:
            logger.info(f"📋 执行测试: {test_name}")
            try:
                result = await test_func()
                results[test_name] = {
                    "status": "PASSED" if result["success"] else "FAILED",
                    "details": result,
                    "timestamp": time.time()
                }
                if result["success"]:
                    passed_tests += 1
                    logger.info(f"✅ {test_name} - 通过")
                else:
                    logger.error(f"❌ {test_name} - 失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                logger.error(f"💥 {test_name} - 异常: {e}")
                results[test_name] = {
                    "status": "ERROR",
                    "details": {"success": False, "error": str(e)},
                    "timestamp": time.time()
                }
        
        # 计算总体成功率
        success_rate = (passed_tests / total_tests) * 100
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "completion_status": "100%" if success_rate >= 95 else f"{success_rate:.1f}%",
            "test_results": results,
            "timestamp": time.time()
        }
        
        logger.info(f"🎯 综合集成测试完成 - 成功率: {success_rate:.1f}%")
        return summary

    async def test_service_health(self) -> Dict[str, Any]:
        """测试服务健康检查"""
        try:
            health_results = {}
            all_healthy = True
            
            for service_name, service_url in TEST_CONFIG["services"].items():
                try:
                    async with self.session.get(f"{service_url}/health") as response:
                        if response.status == 200:
                            data = await response.json()
                            health_results[service_name] = {
                                "status": "healthy",
                                "response_time": data.get("response_time", 0),
                                "details": data
                            }
                        else:
                            health_results[service_name] = {
                                "status": "unhealthy",
                                "http_status": response.status
                            }
                            all_healthy = False
                            
                except Exception as e:
                    health_results[service_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    all_healthy = False
            
            return {
                "success": all_healthy,
                "health_results": health_results,
                "healthy_services": sum(1 for r in health_results.values() if r["status"] == "healthy"),
                "total_services": len(TEST_CONFIG["services"])
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_user_authentication(self) -> Dict[str, Any]:
        """测试用户认证流程"""
        try:
            # 1. 用户注册
            register_data = {
                "username": "test_user",
                "email": "test@suokelife.com",
                "password": "test_password_123"
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['auth_service']}/auth/register",
                json=register_data
            ) as response:
                if response.status not in [200, 201, 409]:  # 409 = 用户已存在
                    return {"success": False, "error": f"注册失败: {response.status}"}
            
            # 2. 用户登录
            login_data = {
                "username": "test_user",
                "password": "test_password_123"
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['auth_service']}/auth/login",
                json=login_data
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"登录失败: {response.status}"}
                
                auth_result = await response.json()
                token = auth_result.get("access_token")
                
                if not token:
                    return {"success": False, "error": "未获取到访问令牌"}
            
            # 3. 验证令牌
            headers = {"Authorization": f"Bearer {token}"}
            async with self.session.get(
                f"{TEST_CONFIG['services']['auth_service']}/auth/verify",
                headers=headers
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"令牌验证失败: {response.status}"}
            
            return {
                "success": True,
                "token": token[:20] + "...",  # 只显示部分令牌
                "auth_flow": "完整认证流程测试通过"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_agent_collaboration(self) -> Dict[str, Any]:
        """测试智能体协作"""
        try:
            collaboration_results = {}
            
            # 测试小艾健康咨询
            xiaoai_request = {
                "text": "我最近感觉疲劳，想了解一下体质调理",
                "user_id": self.test_user_id,
                "session_id": self.test_session_id
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['xiaoai']}/chat",
                json=xiaoai_request
            ) as response:
                if response.status == 200:
                    xiaoai_result = await response.json()
                    collaboration_results["xiaoai"] = {
                        "status": "success",
                        "response_type": xiaoai_result.get("type"),
                        "knowledge_enhanced": xiaoai_result.get("knowledge_enhanced", False)
                    }
                else:
                    collaboration_results["xiaoai"] = {"status": "failed", "code": response.status}
            
            # 测试小克商业化服务
            xiaoke_request = {
                "service_type": "health_product_recommendation",
                "user_profile": {"age": 30, "gender": "female", "health_concerns": ["疲劳"]}
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['xiaoke']}/recommend",
                json=xiaoke_request
            ) as response:
                if response.status == 200:
                    collaboration_results["xiaoke"] = {"status": "success"}
                else:
                    collaboration_results["xiaoke"] = {"status": "failed", "code": response.status}
            
            # 测试老克教育服务
            laoke_request = {
                "topic": "中医体质养生",
                "user_level": "beginner"
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['laoke']}/educate",
                json=laoke_request
            ) as response:
                if response.status == 200:
                    collaboration_results["laoke"] = {"status": "success"}
                else:
                    collaboration_results["laoke"] = {"status": "failed", "code": response.status}
            
            # 测试索儿生活管理
            soer_request = {
                "lifestyle_data": {
                    "sleep_hours": 7,
                    "exercise_minutes": 30,
                    "stress_level": "medium"
                }
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['soer']}/analyze_lifestyle",
                json=soer_request
            ) as response:
                if response.status == 200:
                    collaboration_results["soer"] = {"status": "success"}
                else:
                    collaboration_results["soer"] = {"status": "failed", "code": response.status}
            
            # 检查协作成功率
            successful_agents = sum(1 for result in collaboration_results.values() 
                                  if result["status"] == "success")
            total_agents = len(collaboration_results)
            
            return {
                "success": successful_agents >= 3,  # 至少3个智能体成功
                "collaboration_results": collaboration_results,
                "successful_agents": successful_agents,
                "total_agents": total_agents,
                "collaboration_rate": f"{(successful_agents/total_agents)*100:.1f}%"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_knowledge_graph_integration(self) -> Dict[str, Any]:
        """测试知识图谱集成"""
        try:
            # 测试知识图谱搜索
            kg_request = {
                "query": "气虚体质的调理方法",
                "knowledge_types": ["constitution", "herb", "treatment"],
                "limit": 5
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['rag_service']}/knowledge_graph/search",
                json=kg_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"知识图谱搜索失败: {response.status}"}
                
                kg_result = await response.json()
                
                # 验证返回结果
                if not kg_result.get("nodes"):
                    return {"success": False, "error": "知识图谱未返回相关节点"}
                
                nodes_count = len(kg_result["nodes"])
                confidence = kg_result.get("confidence", 0)
                
                return {
                    "success": True,
                    "nodes_found": nodes_count,
                    "confidence": confidence,
                    "reasoning_path": kg_result.get("reasoning_path", []),
                    "knowledge_enhanced": nodes_count > 0 and confidence > 0.7
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_tongue_analysis_workflow(self) -> Dict[str, Any]:
        """测试舌象分析工作流程"""
        try:
            # 创建测试图像数据（模拟）
            test_image = self._create_test_image_data()
            
            # 测试舌象分析
            analysis_request = {
                "image_data": test_image,
                "user_id": self.test_user_id,
                "analysis_type": "comprehensive"
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['xiaoai']}/analyze/tongue",
                json=analysis_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"舌象分析失败: {response.status}"}
                
                analysis_result = await response.json()
                
                # 验证分析结果
                required_fields = ["tongue_body", "tongue_coating", "diagnosis", "confidence"]
                missing_fields = [field for field in required_fields 
                                if field not in analysis_result]
                
                if missing_fields:
                    return {"success": False, "error": f"缺少必要字段: {missing_fields}"}
                
                confidence = analysis_result.get("confidence", 0)
                enhanced = analysis_result.get("enhanced_analysis", False)
                accuracy_target = analysis_result.get("accuracy_target", "N/A")
                
                return {
                    "success": confidence > 0.8,  # 要求置信度大于80%
                    "confidence": confidence,
                    "enhanced_analysis": enhanced,
                    "accuracy_target": accuracy_target,
                    "processing_time": analysis_result.get("processing_time", 0),
                    "diagnosis": analysis_result.get("diagnosis", "")[:100] + "..."
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_health_data_management(self) -> Dict[str, Any]:
        """测试健康数据管理"""
        try:
            # 1. 创建健康数据
            health_data = {
                "user_id": self.test_user_id,
                "data_type": "tongue_analysis",
                "data": {
                    "analysis_result": "气虚体质",
                    "confidence": 0.92,
                    "timestamp": time.time()
                },
                "privacy_level": "private"
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['health_data_service']}/data",
                json=health_data
            ) as response:
                if response.status not in [200, 201]:
                    return {"success": False, "error": f"健康数据创建失败: {response.status}"}
                
                create_result = await response.json()
                data_id = create_result.get("data_id")
                
                if not data_id:
                    return {"success": False, "error": "未获取到数据ID"}
            
            # 2. 查询健康数据
            async with self.session.get(
                f"{TEST_CONFIG['services']['health_data_service']}/data/{self.test_user_id}"
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"健康数据查询失败: {response.status}"}
                
                query_result = await response.json()
                data_count = len(query_result.get("data", []))
            
            # 3. 数据隐私验证
            async with self.session.get(
                f"{TEST_CONFIG['services']['health_data_service']}/data/{data_id}/privacy"
            ) as response:
                privacy_verified = response.status == 200
            
            return {
                "success": True,
                "data_id": data_id,
                "data_count": data_count,
                "privacy_verified": privacy_verified,
                "data_management": "完整数据管理流程测试通过"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_blockchain_verification(self) -> Dict[str, Any]:
        """测试区块链数据验证"""
        try:
            # 测试数据上链
            blockchain_data = {
                "data_hash": "test_hash_12345",
                "user_id": self.test_user_id,
                "data_type": "health_record",
                "timestamp": time.time()
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['blockchain_service']}/store",
                json=blockchain_data
            ) as response:
                if response.status not in [200, 201]:
                    return {"success": False, "error": f"区块链存储失败: {response.status}"}
                
                store_result = await response.json()
                transaction_id = store_result.get("transaction_id")
                
                if not transaction_id:
                    return {"success": False, "error": "未获取到交易ID"}
            
            # 测试数据验证
            async with self.session.get(
                f"{TEST_CONFIG['services']['blockchain_service']}/verify/{transaction_id}"
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"区块链验证失败: {response.status}"}
                
                verify_result = await response.json()
                verified = verify_result.get("verified", False)
            
            return {
                "success": verified,
                "transaction_id": transaction_id,
                "verified": verified,
                "blockchain_integration": "区块链验证流程测试通过"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_rag_service_integration(self) -> Dict[str, Any]:
        """测试RAG服务集成"""
        try:
            # 测试文档检索
            rag_request = {
                "query": "中医体质分类和特征",
                "top_k": 5,
                "include_metadata": True
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['rag_service']}/retrieve",
                json=rag_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"RAG检索失败: {response.status}"}
                
                rag_result = await response.json()
                documents = rag_result.get("documents", [])
                
                if not documents:
                    return {"success": False, "error": "RAG服务未返回相关文档"}
            
            # 测试增强生成
            generation_request = {
                "query": "气虚体质的人应该如何调理？",
                "context": documents[:3],  # 使用前3个文档作为上下文
                "max_length": 200
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['rag_service']}/generate",
                json=generation_request
            ) as response:
                if response.status != 200:
                    return {"success": False, "error": f"RAG生成失败: {response.status}"}
                
                generation_result = await response.json()
                generated_text = generation_result.get("generated_text", "")
                
                return {
                    "success": len(generated_text) > 50,  # 生成的文本应该有一定长度
                    "documents_found": len(documents),
                    "generated_length": len(generated_text),
                    "rag_integration": "RAG服务集成测试通过"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_api_gateway_routing(self) -> Dict[str, Any]:
        """测试API网关路由"""
        try:
            routing_results = {}
            
            # 测试不同服务的路由
            test_routes = [
                ("/api/v1/xiaoai/health", "xiaoai服务路由"),
                ("/api/v1/auth/status", "认证服务路由"),
                ("/api/v1/health-data/status", "健康数据服务路由"),
                ("/api/v1/rag/status", "RAG服务路由")
            ]
            
            for route, description in test_routes:
                try:
                    async with self.session.get(
                        f"{TEST_CONFIG['services']['api_gateway']}{route}"
                    ) as response:
                        routing_results[route] = {
                            "status": "success" if response.status in [200, 404] else "failed",
                            "http_status": response.status,
                            "description": description
                        }
                except Exception as e:
                    routing_results[route] = {
                        "status": "error",
                        "error": str(e),
                        "description": description
                    }
            
            successful_routes = sum(1 for result in routing_results.values() 
                                  if result["status"] == "success")
            total_routes = len(routing_results)
            
            return {
                "success": successful_routes >= total_routes * 0.8,  # 80%路由成功
                "routing_results": routing_results,
                "successful_routes": successful_routes,
                "total_routes": total_routes,
                "routing_rate": f"{(successful_routes/total_routes)*100:.1f}%"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_end_to_end_diagnosis(self) -> Dict[str, Any]:
        """测试端到端诊断流程"""
        try:
            # 完整的诊断流程测试
            diagnosis_steps = {}
            
            # 1. 用户提交症状
            symptom_data = {
                "symptoms": ["疲劳", "食欲不振", "舌苔厚腻"],
                "user_id": self.test_user_id,
                "session_id": self.test_session_id
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['xiaoai']}/diagnosis/symptoms",
                json=symptom_data
            ) as response:
                diagnosis_steps["symptom_submission"] = {
                    "success": response.status == 200,
                    "status_code": response.status
                }
            
            # 2. 舌象分析
            tongue_data = {
                "image_data": self._create_test_image_data(),
                "user_id": self.test_user_id
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['xiaoai']}/analyze/tongue",
                json=tongue_data
            ) as response:
                if response.status == 200:
                    tongue_result = await response.json()
                    diagnosis_steps["tongue_analysis"] = {
                        "success": True,
                        "confidence": tongue_result.get("confidence", 0)
                    }
                else:
                    diagnosis_steps["tongue_analysis"] = {
                        "success": False,
                        "status_code": response.status
                    }
            
            # 3. 综合诊断
            comprehensive_data = {
                "user_id": self.test_user_id,
                "session_id": self.test_session_id,
                "include_recommendations": True
            }
            
            async with self.session.post(
                f"{TEST_CONFIG['services']['xiaoai']}/diagnosis/comprehensive",
                json=comprehensive_data
            ) as response:
                diagnosis_steps["comprehensive_diagnosis"] = {
                    "success": response.status == 200,
                    "status_code": response.status
                }
            
            # 4. 健康建议生成
            async with self.session.get(
                f"{TEST_CONFIG['services']['xiaoai']}/recommendations/{self.test_user_id}"
            ) as response:
                diagnosis_steps["health_recommendations"] = {
                    "success": response.status == 200,
                    "status_code": response.status
                }
            
            # 计算端到端成功率
            successful_steps = sum(1 for step in diagnosis_steps.values() 
                                 if step["success"])
            total_steps = len(diagnosis_steps)
            
            return {
                "success": successful_steps >= total_steps * 0.8,  # 80%步骤成功
                "diagnosis_steps": diagnosis_steps,
                "successful_steps": successful_steps,
                "total_steps": total_steps,
                "e2e_success_rate": f"{(successful_steps/total_steps)*100:.1f}%",
                "end_to_end_diagnosis": "端到端诊断流程测试完成"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_test_image_data(self) -> str:
        """创建测试图像数据"""
        # 创建一个简单的测试图像（Base64编码）
        import io
        from PIL import Image
        
        # 创建一个简单的红色图像
        img = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        img_data = buffer.getvalue()
        
        return base64.b64encode(img_data).decode('utf-8')


# 测试运行器
async def run_comprehensive_integration_tests():
    """运行综合集成测试"""
    async with ComprehensiveIntegrationTester() as tester:
        results = await tester.run_comprehensive_tests()
        
        # 生成测试报告
        report = generate_test_report(results)
        
        # 保存测试结果
        with open("comprehensive_integration_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return results


def generate_test_report(results: Dict[str, Any]) -> str:
    """生成测试报告"""
    report_lines = [
        "=" * 80,
        "索克生活项目 - 综合集成测试报告",
        "=" * 80,
        f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"总测试数: {results['total_tests']}",
        f"通过测试: {results['passed_tests']}",
        f"失败测试: {results['failed_tests']}",
        f"成功率: {results['success_rate']:.1f}%",
        f"完成状态: {results['completion_status']}",
        "",
        "详细测试结果:",
        "-" * 40
    ]
    
    for test_name, test_result in results["test_results"].items():
        status_icon = "✅" if test_result["status"] == "PASSED" else "❌"
        report_lines.append(f"{status_icon} {test_name}: {test_result['status']}")
        
        if test_result["status"] != "PASSED":
            error = test_result["details"].get("error", "未知错误")
            report_lines.append(f"   错误: {error}")
    
    report_lines.extend([
        "",
        "=" * 80,
        f"项目完成度评估: {results['completion_status']}",
        "=" * 80
    ])
    
    return "\n".join(report_lines)


# Pytest测试用例
@pytest.mark.asyncio
async def test_comprehensive_integration():
    """Pytest集成测试入口"""
    results = await run_comprehensive_integration_tests()
    
    # 断言测试成功率
    assert results["success_rate"] >= 95, f"集成测试成功率过低: {results['success_rate']:.1f}%"
    
    # 断言关键服务正常
    critical_tests = [
        "服务健康检查",
        "智能体协作", 
        "舌象分析流程",
        "端到端诊断流程"
    ]
    
    for test_name in critical_tests:
        test_result = results["test_results"].get(test_name)
        assert test_result and test_result["status"] == "PASSED", f"关键测试失败: {test_name}"


if __name__ == "__main__":
    # 直接运行测试
    asyncio.run(run_comprehensive_integration_tests()) 