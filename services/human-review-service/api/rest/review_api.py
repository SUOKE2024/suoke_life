"""
审核REST API

提供审核任务的CRUD操作和工作流管理，包括：
- 创建审核任务
- 查询审核状态
- 提交审核结果
- 审核任务管理
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from internal.config.settings import get_settings
from internal.models.review_models import (
    ReviewTask, ReviewResult, ReviewStatus, Priority, ContentType, RiskLevel
)
from internal.tasks.ai_tasks import analyze_text_content, generate_review_suggestions

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/v1/reviews", tags=["审核管理"])


# 请求模型
class CreateReviewTaskRequest(BaseModel):
    """创建审核任务请求"""
    content: str = Field(..., description="待审核内容")
    content_type: ContentType = Field(default=ContentType.TEXT, description="内容类型")
    source_id: str = Field(..., description="内容来源ID")
    source_type: str = Field(..., description="内容来源类型")
    submitter_id: str = Field(..., description="提交者ID")
    priority: Priority = Field(default=Priority.MEDIUM, description="优先级")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class SubmitReviewResultRequest(BaseModel):
    """提交审核结果请求"""
    decision: str = Field(..., description="审核决定", regex="^(approved|rejected|needs_revision)$")
    confidence: float = Field(..., description="置信度", ge=0.0, le=1.0)
    comments: Optional[str] = Field(default=None, description="审核意见")
    tags: Optional[List[str]] = Field(default=None, description="标签")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class UpdateReviewTaskRequest(BaseModel):
    """更新审核任务请求"""
    priority: Optional[Priority] = Field(default=None, description="优先级")
    assigned_to: Optional[str] = Field(default=None, description="分配给")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


# 响应模型
class ReviewTaskResponse(BaseModel):
    """审核任务响应"""
    id: str
    content: str
    content_type: str
    source_id: str
    source_type: str
    submitter_id: str
    status: str
    priority: str
    assigned_to: Optional[str]
    ai_analysis: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]


class ReviewResultResponse(BaseModel):
    """审核结果响应"""
    id: str
    task_id: str
    reviewer_id: str
    decision: str
    confidence: float
    comments: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    metadata: Optional[Dict[str, Any]]


class ReviewStatsResponse(BaseModel):
    """审核统计响应"""
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    avg_processing_time: float
    success_rate: float


# API端点
@router.post("/tasks", response_model=ReviewTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_review_task(request: CreateReviewTaskRequest) -> ReviewTaskResponse:
    """创建审核任务"""
    try:
        logger.info(f"创建审核任务，内容类型: {request.content_type}")
        
        # 创建任务ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # 启动AI分析
        ai_task = analyze_text_content.delay(
            content=request.content,
            content_type=request.content_type.value,
            context=request.context
        )
        
        # 创建审核任务（这里应该保存到数据库）
        task_data = {
            'id': task_id,
            'content': request.content,
            'content_type': request.content_type.value,
            'source_id': request.source_id,
            'source_type': request.source_type,
            'submitter_id': request.submitter_id,
            'status': ReviewStatus.PENDING.value,
            'priority': request.priority.value,
            'assigned_to': None,
            'ai_analysis': None,
            'ai_task_id': ai_task.id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'metadata': request.metadata or {}
        }
        
        logger.info(f"审核任务创建成功，ID: {task_id}")
        
        return ReviewTaskResponse(**task_data)
        
    except Exception as e:
        logger.error(f"创建审核任务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建审核任务失败: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=ReviewTaskResponse)
async def get_review_task(task_id: str) -> ReviewTaskResponse:
    """获取审核任务详情"""
    try:
        logger.info(f"获取审核任务详情: {task_id}")
        
        # 这里应该从数据库查询任务
        # 暂时返回模拟数据
        task_data = {
            'id': task_id,
            'content': '示例内容',
            'content_type': ContentType.TEXT.value,
            'source_id': 'source_123',
            'source_type': 'user_post',
            'submitter_id': 'user_456',
            'status': ReviewStatus.PENDING.value,
            'priority': Priority.MEDIUM.value,
            'assigned_to': None,
            'ai_analysis': {
                'overall_score': 0.75,
                'risk_level': 'low',
                'confidence': 0.85
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'metadata': {}
        }
        
        return ReviewTaskResponse(**task_data)
        
    except Exception as e:
        logger.error(f"获取审核任务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"审核任务不存在: {task_id}"
        )


@router.get("/tasks", response_model=List[ReviewTaskResponse])
async def list_review_tasks(
    status: Optional[str] = Query(None, description="任务状态"),
    priority: Optional[str] = Query(None, description="优先级"),
    assigned_to: Optional[str] = Query(None, description="分配给"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
) -> List[ReviewTaskResponse]:
    """获取审核任务列表"""
    try:
        logger.info(f"获取审核任务列表，状态: {status}, 优先级: {priority}")
        
        # 这里应该从数据库查询任务列表
        # 暂时返回模拟数据
        tasks = []
        for i in range(min(limit, 5)):  # 返回最多5个示例任务
            task_data = {
                'id': f'task_{i+1}',
                'content': f'示例内容 {i+1}',
                'content_type': ContentType.TEXT.value,
                'source_id': f'source_{i+1}',
                'source_type': 'user_post',
                'submitter_id': f'user_{i+1}',
                'status': status or ReviewStatus.PENDING.value,
                'priority': priority or Priority.MEDIUM.value,
                'assigned_to': assigned_to,
                'ai_analysis': {
                    'overall_score': 0.75 + i * 0.05,
                    'risk_level': 'low',
                    'confidence': 0.85
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'metadata': {}
            }
            tasks.append(ReviewTaskResponse(**task_data))
        
        return tasks
        
    except Exception as e:
        logger.error(f"获取审核任务列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取审核任务列表失败: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=ReviewTaskResponse)
async def update_review_task(task_id: str, request: UpdateReviewTaskRequest) -> ReviewTaskResponse:
    """更新审核任务"""
    try:
        logger.info(f"更新审核任务: {task_id}")
        
        # 这里应该更新数据库中的任务
        # 暂时返回模拟数据
        task_data = {
            'id': task_id,
            'content': '示例内容',
            'content_type': ContentType.TEXT.value,
            'source_id': 'source_123',
            'source_type': 'user_post',
            'submitter_id': 'user_456',
            'status': ReviewStatus.PENDING.value,
            'priority': request.priority.value if request.priority else Priority.MEDIUM.value,
            'assigned_to': request.assigned_to,
            'ai_analysis': {
                'overall_score': 0.75,
                'risk_level': 'low',
                'confidence': 0.85
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'metadata': request.metadata or {}
        }
        
        logger.info(f"审核任务更新成功: {task_id}")
        
        return ReviewTaskResponse(**task_data)
        
    except Exception as e:
        logger.error(f"更新审核任务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新审核任务失败: {str(e)}"
        )


@router.post("/tasks/{task_id}/assign")
async def assign_review_task(task_id: str, reviewer_id: str) -> Dict[str, Any]:
    """分配审核任务"""
    try:
        logger.info(f"分配审核任务: {task_id} -> {reviewer_id}")
        
        # 这里应该更新数据库中的任务分配
        # 暂时返回成功响应
        
        return {
            'success': True,
            'message': f'任务 {task_id} 已分配给 {reviewer_id}',
            'task_id': task_id,
            'reviewer_id': reviewer_id,
            'assigned_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"分配审核任务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分配审核任务失败: {str(e)}"
        )


@router.post("/tasks/{task_id}/results", response_model=ReviewResultResponse, status_code=status.HTTP_201_CREATED)
async def submit_review_result(task_id: str, request: SubmitReviewResultRequest, reviewer_id: str = "current_user") -> ReviewResultResponse:
    """提交审核结果"""
    try:
        logger.info(f"提交审核结果，任务: {task_id}, 审核员: {reviewer_id}")
        
        # 创建结果ID
        import uuid
        result_id = str(uuid.uuid4())
        
        # 创建审核结果（这里应该保存到数据库）
        result_data = {
            'id': result_id,
            'task_id': task_id,
            'reviewer_id': reviewer_id,
            'decision': request.decision,
            'confidence': request.confidence,
            'comments': request.comments,
            'tags': request.tags,
            'created_at': datetime.utcnow(),
            'metadata': request.metadata or {}
        }
        
        # 更新任务状态为已完成
        # 这里应该更新数据库中的任务状态
        
        logger.info(f"审核结果提交成功，结果ID: {result_id}")
        
        return ReviewResultResponse(**result_data)
        
    except Exception as e:
        logger.error(f"提交审核结果失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交审核结果失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/results", response_model=List[ReviewResultResponse])
async def get_review_results(task_id: str) -> List[ReviewResultResponse]:
    """获取审核结果"""
    try:
        logger.info(f"获取审核结果: {task_id}")
        
        # 这里应该从数据库查询审核结果
        # 暂时返回模拟数据
        results = [
            ReviewResultResponse(
                id="result_1",
                task_id=task_id,
                reviewer_id="reviewer_1",
                decision="approved",
                confidence=0.9,
                comments="内容质量良好，符合规范",
                tags=["quality", "approved"],
                created_at=datetime.utcnow(),
                metadata={}
            )
        ]
        
        return results
        
    except Exception as e:
        logger.error(f"获取审核结果失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取审核结果失败: {str(e)}"
        )


@router.get("/stats", response_model=ReviewStatsResponse)
async def get_review_stats() -> ReviewStatsResponse:
    """获取审核统计"""
    try:
        logger.info("获取审核统计")
        
        # 这里应该从数据库查询统计数据
        # 暂时返回模拟数据
        stats = ReviewStatsResponse(
            total_tasks=1000,
            pending_tasks=50,
            in_progress_tasks=25,
            completed_tasks=925,
            avg_processing_time=15.5,  # 分钟
            success_rate=0.95
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"获取审核统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取审核统计失败: {str(e)}"
        )


@router.post("/tasks/{task_id}/ai-suggestions")
async def get_ai_suggestions(task_id: str) -> Dict[str, Any]:
    """获取AI审核建议"""
    try:
        logger.info(f"获取AI审核建议: {task_id}")
        
        # 这里应该从数据库获取任务内容和AI分析结果
        # 暂时使用模拟数据
        content = "示例内容"
        analysis_result = {
            'overall_score': 0.75,
            'risk_level': 'low',
            'confidence': 0.85,
            'quality': {'score': 0.8},
            'compliance': {'is_compliant': True, 'violations': []},
            'medical': {'is_medical_content': False}
        }
        
        # 生成审核建议
        suggestions_task = generate_review_suggestions.delay(content, analysis_result)
        suggestions_result = suggestions_task.get(timeout=30)
        
        return {
            'success': True,
            'task_id': task_id,
            'suggestions': suggestions_result
        }
        
    except Exception as e:
        logger.error(f"获取AI审核建议失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取AI审核建议失败: {str(e)}"
        )


@router.post("/tasks/batch")
async def create_batch_review_tasks(requests: List[CreateReviewTaskRequest]) -> Dict[str, Any]:
    """批量创建审核任务"""
    try:
        logger.info(f"批量创建审核任务，数量: {len(requests)}")
        
        task_ids = []
        for request in requests:
            # 创建任务ID
            import uuid
            task_id = str(uuid.uuid4())
            task_ids.append(task_id)
            
            # 启动AI分析
            analyze_text_content.delay(
                content=request.content,
                content_type=request.content_type.value,
                context=request.context
            )
        
        logger.info(f"批量创建审核任务成功，创建了 {len(task_ids)} 个任务")
        
        return {
            'success': True,
            'created_count': len(task_ids),
            'task_ids': task_ids
        }
        
    except Exception as e:
        logger.error(f"批量创建审核任务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量创建审核任务失败: {str(e)}"
        ) 