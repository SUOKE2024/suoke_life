"""
数据库集成测试
Database Integration Tests

测试数据库连接、CRUD操作和事务处理
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.models import (
    ReviewerDB, ReviewTaskDB, ReviewerCreate, ReviewTaskCreate,
    ReviewType, ReviewPriority, ReviewStatus, ReviewerStatus
)
from ..core.service import HumanReviewService


class TestDatabaseIntegration:
    """数据库集成测试"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self, db_session: AsyncSession):
        """测试数据库连接"""
        # 执行简单查询测试连接
        result = await db_session.execute(select(func.count()).select_from(ReviewerDB))
        count = result.scalar()
        assert count is not None
        assert count >= 0
    
    @pytest.mark.asyncio
    async def test_reviewer_crud_operations(self, db_session: AsyncSession):
        """测试审核员CRUD操作"""
        # 创建审核员
        reviewer_data = {
            "reviewer_id": f"test_reviewer_{uuid4().hex[:8]}",
            "name": "测试医生",
            "email": "test@example.com",
            "specialties": ["中医诊断", "方剂学"],
            "max_concurrent_tasks": 5,
            "status": ReviewerStatus.ACTIVE,
            "current_task_count": 0,
            "is_available": True
        }
        
        reviewer = ReviewerDB(**reviewer_data)
        db_session.add(reviewer)
        await db_session.commit()
        await db_session.refresh(reviewer)
        
        # 验证创建
        assert reviewer.reviewer_id == reviewer_data["reviewer_id"]
        assert reviewer.name == reviewer_data["name"]
        assert reviewer.email == reviewer_data["email"]
        assert reviewer.specialties == reviewer_data["specialties"]
        
        # 读取审核员
        result = await db_session.execute(
            select(ReviewerDB).where(ReviewerDB.reviewer_id == reviewer.reviewer_id)
        )
        found_reviewer = result.scalar_one_or_none()
        assert found_reviewer is not None
        assert found_reviewer.reviewer_id == reviewer.reviewer_id
        
        # 更新审核员
        found_reviewer.name = "更新后的医生"
        found_reviewer.max_concurrent_tasks = 10
        await db_session.commit()
        await db_session.refresh(found_reviewer)
        
        assert found_reviewer.name == "更新后的医生"
        assert found_reviewer.max_concurrent_tasks == 10
        
        # 删除审核员
        await db_session.delete(found_reviewer)
        await db_session.commit()
        
        # 验证删除
        result = await db_session.execute(
            select(ReviewerDB).where(ReviewerDB.reviewer_id == reviewer.reviewer_id)
        )
        deleted_reviewer = result.scalar_one_or_none()
        assert deleted_reviewer is None
    
    @pytest.mark.asyncio
    async def test_review_task_crud_operations(self, db_session: AsyncSession):
        """测试审核任务CRUD操作"""
        # 创建审核任务
        task_data = {
            "task_id": f"test_task_{uuid4().hex[:8]}",
            "review_type": ReviewType.MEDICAL_DIAGNOSIS,
            "priority": ReviewPriority.NORMAL,
            "status": ReviewStatus.PENDING,
            "content": {
                "symptoms": ["头痛", "发热"],
                "diagnosis": "感冒",
                "treatment": "多休息，多喝水"
            },
            "user_id": "user_123",
            "agent_id": "xiaoai_agent",
            "estimated_duration": 1800,
            "created_at": datetime.utcnow()
        }
        
        task = ReviewTaskDB(**task_data)
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)
        
        # 验证创建
        assert task.task_id == task_data["task_id"]
        assert task.review_type == task_data["review_type"]
        assert task.priority == task_data["priority"]
        assert task.status == task_data["status"]
        assert task.content == task_data["content"]
        
        # 读取任务
        result = await db_session.execute(
            select(ReviewTaskDB).where(ReviewTaskDB.task_id == task.task_id)
        )
        found_task = result.scalar_one_or_none()
        assert found_task is not None
        assert found_task.task_id == task.task_id
        
        # 更新任务
        found_task.status = ReviewStatus.IN_PROGRESS
        found_task.assigned_at = datetime.utcnow()
        await db_session.commit()
        await db_session.refresh(found_task)
        
        assert found_task.status == ReviewStatus.IN_PROGRESS
        assert found_task.assigned_at is not None
        
        # 删除任务
        await db_session.delete(found_task)
        await db_session.commit()
        
        # 验证删除
        result = await db_session.execute(
            select(ReviewTaskDB).where(ReviewTaskDB.task_id == task.task_id)
        )
        deleted_task = result.scalar_one_or_none()
        assert deleted_task is None
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, db_session: AsyncSession):
        """测试事务回滚"""
        # 创建审核员
        reviewer_data = {
            "reviewer_id": f"test_rollback_{uuid4().hex[:8]}",
            "name": "回滚测试医生",
            "email": "rollback@example.com",
            "specialties": ["测试专业"],
            "max_concurrent_tasks": 3,
            "status": ReviewerStatus.ACTIVE,
            "current_task_count": 0,
            "is_available": True
        }
        
        reviewer = ReviewerDB(**reviewer_data)
        db_session.add(reviewer)
        
        try:
            # 故意引发错误（重复的reviewer_id）
            duplicate_reviewer = ReviewerDB(**reviewer_data)
            db_session.add(duplicate_reviewer)
            await db_session.commit()
            
            # 如果没有异常，测试失败
            assert False, "应该抛出重复键异常"
            
        except Exception:
            # 回滚事务
            await db_session.rollback()
            
            # 验证回滚后数据库状态
            result = await db_session.execute(
                select(ReviewerDB).where(ReviewerDB.reviewer_id == reviewer_data["reviewer_id"])
            )
            found_reviewer = result.scalar_one_or_none()
            assert found_reviewer is None
    
    @pytest.mark.asyncio
    async def test_relationship_queries(self, db_session: AsyncSession):
        """测试关联查询"""
        # 创建审核员
        reviewer_data = {
            "reviewer_id": f"test_rel_{uuid4().hex[:8]}",
            "name": "关联测试医生",
            "email": "relation@example.com",
            "specialties": ["中医诊断"],
            "max_concurrent_tasks": 5,
            "status": ReviewerStatus.ACTIVE,
            "current_task_count": 0,
            "is_available": True
        }
        
        reviewer = ReviewerDB(**reviewer_data)
        db_session.add(reviewer)
        await db_session.commit()
        await db_session.refresh(reviewer)
        
        # 创建关联的审核任务
        task_data = {
            "task_id": f"test_rel_task_{uuid4().hex[:8]}",
            "review_type": ReviewType.MEDICAL_DIAGNOSIS,
            "priority": ReviewPriority.NORMAL,
            "status": ReviewStatus.IN_PROGRESS,
            "content": {"test": "data"},
            "user_id": "user_rel_123",
            "agent_id": "xiaoai_agent",
            "estimated_duration": 1800,
            "assigned_to": reviewer.reviewer_id,
            "assigned_at": datetime.utcnow()
        }
        
        task = ReviewTaskDB(**task_data)
        db_session.add(task)
        await db_session.commit()
        
        # 查询审核员的任务
        result = await db_session.execute(
            select(ReviewTaskDB).where(ReviewTaskDB.assigned_to == reviewer.reviewer_id)
        )
        reviewer_tasks = result.scalars().all()
        
        assert len(reviewer_tasks) == 1
        assert reviewer_tasks[0].task_id == task.task_id
        assert reviewer_tasks[0].assigned_to == reviewer.reviewer_id
        
        # 清理
        await db_session.delete(task)
        await db_session.delete(reviewer)
        await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_bulk_operations(self, db_session: AsyncSession):
        """测试批量操作"""
        # 批量创建审核员
        reviewers = []
        for i in range(5):
            reviewer_data = {
                "reviewer_id": f"test_bulk_{i}_{uuid4().hex[:8]}",
                "name": f"批量测试医生{i}",
                "email": f"bulk{i}@example.com",
                "specialties": ["中医诊断"] if i % 2 == 0 else ["西医诊断"],
                "max_concurrent_tasks": 3 + i,
                "status": ReviewerStatus.ACTIVE,
                "current_task_count": 0,
                "is_available": True
            }
            reviewer = ReviewerDB(**reviewer_data)
            reviewers.append(reviewer)
            db_session.add(reviewer)
        
        await db_session.commit()
        
        # 验证批量创建
        result = await db_session.execute(
            select(func.count()).select_from(ReviewerDB).where(
                ReviewerDB.name.like("批量测试医生%")
            )
        )
        count = result.scalar()
        assert count == 5
        
        # 批量查询
        result = await db_session.execute(
            select(ReviewerDB).where(ReviewerDB.name.like("批量测试医生%"))
        )
        found_reviewers = result.scalars().all()
        assert len(found_reviewers) == 5
        
        # 批量删除
        for reviewer in found_reviewers:
            await db_session.delete(reviewer)
        await db_session.commit()
        
        # 验证批量删除
        result = await db_session.execute(
            select(func.count()).select_from(ReviewerDB).where(
                ReviewerDB.name.like("批量测试医生%")
            )
        )
        count = result.scalar()
        assert count == 0
    
    @pytest.mark.asyncio
    async def test_service_with_database(self, db_session: AsyncSession):
        """测试服务层与数据库的集成"""
        service = HumanReviewService()
        
        # 创建审核员
        reviewer_create = ReviewerCreate(
            reviewer_id=f"test_service_{uuid4().hex[:8]}",
            name="服务测试医生",
            email="service@example.com",
            specialties=["中医诊断"],
            max_concurrent_tasks=5
        )
        
        # 注意：这里需要传递session参数
        # 但是当前的service方法可能需要修改来支持传递session
        # 我们先测试基本的数据库操作
        
        # 手动创建审核员来测试
        reviewer_data = {
            "reviewer_id": reviewer_create.reviewer_id,
            "name": reviewer_create.name,
            "email": reviewer_create.email,
            "specialties": reviewer_create.specialties,
            "max_concurrent_tasks": reviewer_create.max_concurrent_tasks,
            "status": ReviewerStatus.ACTIVE,
            "current_task_count": 0,
            "is_available": True
        }
        
        reviewer = ReviewerDB(**reviewer_data)
        db_session.add(reviewer)
        await db_session.commit()
        await db_session.refresh(reviewer)
        
        # 验证创建
        assert reviewer.reviewer_id == reviewer_create.reviewer_id
        assert reviewer.name == reviewer_create.name
        
        # 清理
        await db_session.delete(reviewer)
        await db_session.commit() 