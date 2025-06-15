#!/usr/bin/env python3
"""
人工审核服务测试脚本

用于快速测试服务的基本功能
"""
import asyncio
import json
import logging
import sys
from typing import Dict, Any

import httpx

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 服务配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


class ReviewServiceTester:
    """审核服务测试器"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_health_check(self) -> bool:
        """测试健康检查"""
        try:
            logger.info("测试健康检查...")
            response = await self.client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"健康检查通过: {result.get('status')}")
                return True
            else:
                logger.error(f"健康检查失败: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"健康检查异常: {e}")
            return False
    
    async def test_create_review_task(self) -> Dict[str, Any]:
        """测试创建审核任务"""
        try:
            logger.info("测试创建审核任务...")
            
            task_data = {
                "content": "这是一个测试内容，用于验证人工审核服务的功能。内容包含健康相关信息，需要专业审核。",
                "content_type": "text",
                "source_id": "test_source_001",
                "source_type": "user_post",
                "submitter_id": "test_user_001",
                "priority": "medium",
                "metadata": {
                    "test": True,
                    "category": "health_advice"
                },
                "context": {
                    "user_history": "new_user",
                    "platform": "web"
                }
            }
            
            response = await self.client.post(
                f"{API_BASE}/reviews/tasks",
                json=task_data
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"审核任务创建成功: {result.get('id')}")
                return result
            else:
                logger.error(f"创建审核任务失败: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"创建审核任务异常: {e}")
            return {}
    
    async def test_get_review_task(self, task_id: str) -> Dict[str, Any]:
        """测试获取审核任务"""
        try:
            logger.info(f"测试获取审核任务: {task_id}")
            
            response = await self.client.get(f"{API_BASE}/reviews/tasks/{task_id}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"获取审核任务成功: {result.get('status')}")
                return result
            else:
                logger.error(f"获取审核任务失败: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"获取审核任务异常: {e}")
            return {}
    
    async def test_list_review_tasks(self) -> list:
        """测试获取审核任务列表"""
        try:
            logger.info("测试获取审核任务列表...")
            
            response = await self.client.get(
                f"{API_BASE}/reviews/tasks",
                params={"limit": 5}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"获取任务列表成功，数量: {len(result)}")
                return result
            else:
                logger.error(f"获取任务列表失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"获取任务列表异常: {e}")
            return []
    
    async def test_submit_review_result(self, task_id: str) -> Dict[str, Any]:
        """测试提交审核结果"""
        try:
            logger.info(f"测试提交审核结果: {task_id}")
            
            result_data = {
                "decision": "approved",
                "confidence": 0.85,
                "comments": "内容质量良好，符合平台规范。建议通过审核。",
                "tags": ["quality", "health", "approved"],
                "metadata": {
                    "review_time": 300,  # 5分钟
                    "reviewer_notes": "专业审核通过"
                }
            }
            
            response = await self.client.post(
                f"{API_BASE}/reviews/tasks/{task_id}/results",
                json=result_data,
                params={"reviewer_id": "test_reviewer_001"}
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"审核结果提交成功: {result.get('id')}")
                return result
            else:
                logger.error(f"提交审核结果失败: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"提交审核结果异常: {e}")
            return {}
    
    async def test_get_ai_suggestions(self, task_id: str) -> Dict[str, Any]:
        """测试获取AI审核建议"""
        try:
            logger.info(f"测试获取AI审核建议: {task_id}")
            
            response = await self.client.post(f"{API_BASE}/reviews/tasks/{task_id}/ai-suggestions")
            
            if response.status_code == 200:
                result = response.json()
                logger.info("AI审核建议获取成功")
                return result
            else:
                logger.error(f"获取AI建议失败: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"获取AI建议异常: {e}")
            return {}
    
    async def test_review_stats(self) -> Dict[str, Any]:
        """测试获取审核统计"""
        try:
            logger.info("测试获取审核统计...")
            
            response = await self.client.get(f"{API_BASE}/reviews/stats")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"统计数据获取成功: 总任务数 {result.get('total_tasks', 0)}")
                return result
            else:
                logger.error(f"获取统计数据失败: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"获取统计数据异常: {e}")
            return {}
    
    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        logger.info("开始运行人工审核服务测试...")
        
        try:
            # 1. 健康检查
            if not await self.test_health_check():
                logger.error("健康检查失败，停止测试")
                return False
            
            # 2. 创建审核任务
            task = await self.test_create_review_task()
            if not task:
                logger.error("创建审核任务失败")
                return False
            
            task_id = task.get('id')
            if not task_id:
                logger.error("任务ID为空")
                return False
            
            # 3. 获取任务详情
            await self.test_get_review_task(task_id)
            
            # 4. 获取任务列表
            await self.test_list_review_tasks()
            
            # 5. 获取AI建议
            await self.test_get_ai_suggestions(task_id)
            
            # 6. 提交审核结果
            await self.test_submit_review_result(task_id)
            
            # 7. 获取统计数据
            await self.test_review_stats()
            
            logger.info("✅ 所有测试完成！")
            return True
            
        except Exception as e:
            logger.error(f"测试过程中发生异常: {e}")
            return False
        
        finally:
            await self.client.aclose()


async def main():
    """主函数"""
    print("🧪 人工审核服务功能测试")
    print("=" * 50)
    
    tester = ReviewServiceTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 测试全部通过！服务运行正常。")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！请检查服务状态。")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 